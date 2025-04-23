#include "llvm/Analysis/BlockFrequencyInfo.h"
#include "llvm/Analysis/BranchProbabilityInfo.h"
#include "llvm/Analysis/LoopAnalysisManager.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Analysis/ScalarEvolution.h"
#include "llvm/Analysis/ScalarEvolutionExpressions.h"
#include "llvm/IR/CFG.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/raw_ostream.h"

#include <iostream>
#include <optional>
#include <queue> // for BFS queue
#include <set>   // to track visited blocks
#include <unordered_map>
#include <vector>

using namespace llvm;

namespace {

    // New helper functions for printing loop-specific CFG and DFG.
    void printLoopCFG(Loop *L, raw_fd_ostream &Out,
                      const std::unordered_map<const BasicBlock *, unsigned> &BBIndexMap) {
        Out << "  Loop CFG:\n";
        for (BasicBlock *BB : L->getBlocks()) {
            unsigned bbIndex = BBIndexMap.at(BB);
            Out << "    Block " << bbIndex << " ("
                << (BB->hasName() ? BB->getName().str() : "bb_" + std::to_string(bbIndex))
                << ") -> Successors: [";
            bool first = true;
            for (const BasicBlock *Succ : successors(BB)) {
                // Include successor only if it is within the current loop.
                if (L->contains(const_cast<BasicBlock *>(Succ))) {
                    if (!first)
                        Out << ", ";
                    Out << BBIndexMap.at(Succ);
                    first = false;
                }
            }
            Out << "]\n";
        }
    }

    void printLoopDFG(Loop *L, raw_fd_ostream &Out) {
        Out << "  Loop DFG:\n";
        // Create a mapping for instructions within the loop.
        std::unordered_map<const Instruction *, unsigned> LoopInstToID;
        unsigned instCounter = 0;
        for (BasicBlock *BB : L->getBlocks()) {
            for (Instruction &I : *BB) {
                LoopInstToID[&I] = instCounter++;
            }
        }
        // Now, for each instruction in the loop, print def-use edges where both
        // the source and destination instructions belong to the loop.
        for (BasicBlock *BB : L->getBlocks()) {
            for (Instruction &Inst : *BB) {
                unsigned dstID = LoopInstToID[&Inst];
                for (unsigned op = 0; op < Inst.getNumOperands(); op++) {
                    if (Instruction *srcInst = dyn_cast<Instruction>(Inst.getOperand(op))) {
                        // Only show edge if the source instruction is part of the loop.
                        if (L->contains(srcInst->getParent()) && LoopInstToID.find(srcInst) != LoopInstToID.end()) {
                            unsigned srcID = LoopInstToID[srcInst];
                            Out << "    " << srcID << " -> " << dstID << "\n";
                        }
                    }
                }
            }
        }
    }

    class LoopAnalysisPass : public PassInfoMixin<LoopAnalysisPass> {
    public:
        // Mapping from BasicBlock pointer to its BFS index (computed in CFG analysis)
        std::unordered_map<const BasicBlock *, unsigned> FunctionBBIndexMap;

        PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
            std::error_code EC;
            raw_fd_ostream Out("ml_features.txt", EC, sys::fs::OF_Text | sys::fs::OF_Append);
            if (EC) {
                errs() << "Error opening ml_features.txt: " << EC.message() << "\n";
                return PreservedAnalyses::all();
            }

            // Out << "=== Function: " << F.getName() << " ===\n";

            // Global CFG(optional)
            analyzeFunctionCFG(F, Out);

            // Global DFG(optional)
            analyzeDFG(F, Out);

            // Loop analysis
            LoopInfo &LI = FAM.getResult<LoopAnalysis>(F);
            ScalarEvolution &SE = FAM.getResult<ScalarEvolutionAnalysis>(F);
            if (!LI.empty()) {
                for (Loop *L : LI)
                    analyzeLoop(L, SE, Out);
            }
            // Out << "=== End Function: " << F.getName() << " ===\n\n";
            Out.flush();
            return PreservedAnalyses::all();
        }

    private:
        // Unmodified global CFG analysis (for context)
        void analyzeFunctionCFG(Function &F, raw_fd_ostream &Out) {
            // Out << "=== Linearized CFG for Function: " << F.getName() << " ===\n";
            if (F.empty()) {
                // Out << "  (Function has no basic blocks)\n\n";
                return;
            }

            BasicBlock &EntryBlock = F.getEntryBlock();
            std::queue<const BasicBlock *> Q;
            std::set<const BasicBlock *> Visited;
            std::vector<const BasicBlock *> BFSOrder;

            Q.push(&EntryBlock);
            Visited.insert(&EntryBlock);

            while (!Q.empty()) {
                const BasicBlock *Curr = Q.front();
                Q.pop();
                BFSOrder.push_back(Curr);
                for (const BasicBlock *Succ : successors(Curr))
                    if (!Visited.count(Succ)) {
                        Visited.insert(Succ);
                        Q.push(Succ);
                    }
            }

            FunctionBBIndexMap.clear();
            for (unsigned i = 0; i < BFSOrder.size(); i++)
                FunctionBBIndexMap[BFSOrder[i]] = i;

            // ... (printing block-level statistics remains the same)
            for (unsigned i = 0; i < BFSOrder.size(); i++) {
                const BasicBlock *BB = BFSOrder[i];
                // Out << "  BlockIndex " << i << ": "
                //      << (BB->hasName() ? BB->getName().str() : ("bb_" + std::to_string(i))) << "\n";
                //  Out << "    Successors=[";
                bool first = true;
                for (const BasicBlock *Succ : successors(BB)) {
                    if (FunctionBBIndexMap.find(Succ) != FunctionBBIndexMap.end()) {
                        if (!first)
                            //     Out << ", ";
                            // Out << FunctionBBIndexMap[Succ];
                            first = false;
                    }
                }
                // Out << "]\n";
            }
            // Out << "=== End of Linearized CFG for " << F.getName() << " ===\n\n";
        }

        // Unmodified global DFG analysis (for context)
        void analyzeDFG(Function &F, raw_fd_ostream &Out) {
            // Out << "=== DFG Analysis for Function: " << F.getName() << " ===\n";
            std::unordered_map<const Instruction *, unsigned> InstToID;
            unsigned instCounter = 0;
            for (auto &BB : F)
                for (auto &Inst : BB)
                    InstToID[&Inst] = instCounter++;

            for (auto &BB : F)
                for (auto &Inst : BB) {
                    unsigned dstID = InstToID[&Inst];
                    for (unsigned op = 0, n = Inst.getNumOperands(); op < n; op++) {
                        if (Instruction *srcInst = dyn_cast<Instruction>(Inst.getOperand(op)))
                            if (InstToID.find(srcInst) != InstToID.end()) {
                            }
                        // Out << InstToID[srcInst] << " -> " << dstID << "\n";
                    }
                }
            // Out << "=== End of DFG for " << F.getName() << " ===\n\n";
        }

        // Modified loop analysis that now includes loop-specific CFG and DFG outputs.
        static unsigned LoopCounter;
        void analyzeLoop(Loop *L, ScalarEvolution &SE, raw_fd_ostream &Out) {
            unsigned currentLoopID = LoopCounter++;
            BasicBlock *Header = L->getHeader();
            std::string HeaderStr = (Header && Header->hasName())
                                        ? Header->getName().str()
                                        : ("bb_" + std::to_string(FunctionBBIndexMap[Header]));

            // Basic loop statistics
            unsigned NumInsts = 0, NumLoads = 0, NumStores = 0, NumBranches = 0;
            for (BasicBlock *BB : L->getBlocks())
                for (Instruction &I : *BB) {
                    ++NumInsts;
                    if (isa<LoadInst>(I))
                        ++NumLoads;
                    if (isa<StoreInst>(I))
                        ++NumStores;
                    if (isa<BranchInst>(I))
                        ++NumBranches;
                }

            const SCEV *BackedgeCount = SE.getBackedgeTakenCount(L);
            std::optional<uint64_t> IterCount = std::nullopt;
            if (!isa<SCEVCouldNotCompute>(BackedgeCount)) {
                if (auto *C = dyn_cast<SCEVConstant>(BackedgeCount))
                    IterCount = C->getAPInt().getZExtValue() + 1;
            }

            // Print loop header and statistics.
            Out << "=== Loop Analysis (ID: " << currentLoopID
                << ", Header: " << HeaderStr << ") ===\n";
            Out << "  Loop depth: " << L->getLoopDepth() << "\n";
            Out << "  NumBlocks: " << L->getNumBlocks() << "\n";
            Out << "  Basic blocks in loop: ";
            bool first = true;
            for (BasicBlock *BB : L->getBlocks()) {
                if (!first)
                    Out << ", ";
                Out << FunctionBBIndexMap[BB];
                first = false;
            }
            Out << "\n";
            Out << "  NumInstructions: " << NumInsts << "\n"
                << "    - Loads:  " << NumLoads << "\n"
                << "    - Stores: " << NumStores << "\n"
                << "    - Branches: " << NumBranches << "\n";

            // Print the loop-specific CFG.
            printLoopCFG(L, Out, FunctionBBIndexMap);

            // Print the loop-specific DFG.
            printLoopDFG(L, Out);

            Out << "\n";

            // Recursively process any nested subloops.
            for (Loop *SubLoop : L->getSubLoops()) {
                analyzeLoop(SubLoop, SE, Out);
            }
        }
    };

    unsigned LoopAnalysisPass::LoopCounter = 0;

} // end anonymous namespace

// Registration for the LLVM pass plugin.
llvm::PassPluginLibraryInfo getLoopAnalysisPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION, "LoopAnalysisPass", "v0.1",
        [](PassBuilder &PB) {
            // Register the pass with the pass pipeline.
            PB.registerPipelineParsingCallback(
                [](StringRef Name, FunctionPassManager &FPM,
                   ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "loop-analysis") {
                        FPM.addPass(LoopAnalysisPass());
                        return true;
                    }
                    return false;
                });
        }};
}

// This is the core interface for pass plugins.
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return getLoopAnalysisPassPluginInfo();
}
