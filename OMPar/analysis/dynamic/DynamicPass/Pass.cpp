#include "llvm/Analysis/BlockFrequencyInfo.h"
#include "llvm/Analysis/BranchProbabilityInfo.h"
#include "llvm/Analysis/LoopAnalysisManager.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/IR/CFG.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/raw_ostream.h"

#include <iostream>
#include <queue>
#include <set>
#include <unordered_map>
#include <vector>

using namespace llvm;

namespace {

    struct DynamicLoopPass : public PassInfoMixin<DynamicLoopPass> {
        // Counter to assign a unique ID to each loop.
        unsigned LoopCounter = 0;

        PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
            std::error_code EC;
            raw_fd_ostream outFile("ml_features.txt", EC, sys::fs::OF_Text | sys::fs::OF_Append);
            if (EC) {
                outFile << "Error opening ml_features.txt: " << EC.message() << "\n";
                return PreservedAnalyses::all();
            }

            // Retrieve required analyses.
            auto &BFI = FAM.getResult<BlockFrequencyAnalysis>(F);
            auto &LI = FAM.getResult<LoopAnalysis>(F);

            outFile << "=== Function: " << F.getName() << " ===\n";

            if (LI.empty()) {
                outFile << "  [No loops found in function]\n";
            } else {
                // Process each top-level loop.
                for (Loop *L : LI)
                    processLoop(L, outFile, BFI);
            }
            outFile << "=== End Function: " << F.getName() << " ===\n\n";
            return PreservedAnalyses::all();
        }

        // Recursively process each loop.
        void processLoop(Loop *L, raw_fd_ostream &outFile, BlockFrequencyAnalysis::Result &BFI, unsigned Depth = 0) {
            // Indentation based on loop depth.
            std::string Indent(Depth * 2, ' ');

            // Assign a unique ID for this loop.
            unsigned thisLoopID = LoopCounter++;

            // Print a header for this loop including its unique ID.
            outFile << Indent << "=== Loop (ID: " << thisLoopID << "): ";
            if (BasicBlock *Header = L->getHeader()) {
                Header->printAsOperand(outFile, false);
            } else {
                outFile << "[Unknown Header]";
            }
            outFile << " (Depth = " << L->getLoopDepth() << ") ===\n";

            // --- Branch Counts within the Loop ---
            outFile << Indent << "--- Branch Counts ---\n";
            for (BasicBlock *BB : L->getBlocks()) {
                if (BranchInst *BI = dyn_cast<BranchInst>(BB->getTerminator())) {
                    if (BI->getNumSuccessors() > 0) {
                        uint64_t BBFreq = BFI.getBlockFreq(BB).getFrequency();
                        outFile << Indent << "  ";
                        BB->printAsOperand(outFile, false);
                        outFile << ": Frequency = " << BBFreq << "\n";
                    }
                }
            }

            // --- Data Access Counts within the Loop ---
            outFile << Indent << "--- Data Access Count ---\n";
            for (BasicBlock *BB : L->getBlocks()) {
                uint64_t BBFreq = BFI.getBlockFreq(BB).getFrequency();
                unsigned numInstr = BB->size();
                unsigned numLoads = 0, numStores = 0;
                outFile << Indent << "  BasicBlock ";
                BB->printAsOperand(outFile, false);
                outFile << ": Frequency = " << BBFreq << "\n";
                outFile << Indent << "    Instr count: " << numInstr << " x " << BBFreq
                        << " = " << (numInstr * BBFreq) << "\n";
                for (Instruction &I : *BB) {
                    if (isa<LoadInst>(I)) {
                        numLoads++;
                        outFile << Indent << "      load from: ";
                        I.getOperand(0)->printAsOperand(outFile, false);
                        outFile << "\n";
                    } else if (isa<StoreInst>(I)) {
                        numStores++;
                        outFile << Indent << "      store to: ";
                        I.getOperand(1)->printAsOperand(outFile, false);
                        outFile << "\n";
                    }
                }
                outFile << Indent << "    Load count: " << numLoads << " x " << BBFreq
                        << " = " << (numLoads * BBFreq) << "\n";
                outFile << Indent << "    Store count: " << numStores << " x " << BBFreq
                        << " = " << (numStores * BBFreq) << "\n\n";
            }

            // Process any nested (sub) loops.
            for (Loop *SubLoop : L->getSubLoops()) {
                processLoop(SubLoop, outFile, BFI, Depth + 1);
            }
        }
    };

} // end anonymous namespace

// Registration for the LLVM pass plugin.
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION, "DynamicLoopPass", "v0.1",
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "dynamic-analysis") {
                        FPM.addPass(DynamicLoopPass());
                        return true;
                    }
                    return false;
                });
        }};
}
