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

    class LoopAnalysisPass : public PassInfoMixin<LoopAnalysisPass> {
    public:
        // Mapping from BasicBlock pointer to its BFS index (computed in CFG analysis)
        std::unordered_map<const BasicBlock *, unsigned> FunctionBBIndexMap;

        PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
            // Open output file "ml_features.txt" in append mode.
            std::error_code EC;
            raw_fd_ostream Out("ml_features.txt", EC, sys::fs::OF_Text | sys::fs::OF_Append);
            if (EC) {
                errs() << "Error opening ml_features.txt: " << EC.message() << "\n";
                return PreservedAnalyses::all();
            }

            Out << "=== Function: " << F.getName() << " ===\n";

            // 1) Emit a BFS-based "linearized" CFG for the entire function.
            analyzeFunctionCFG(F, Out);

            // 2) Perform a simple DFG analysis (def-use relations among instructions).
            analyzeDFG(F, Out);

            // 3) Loop analysis.
            LoopInfo &LI = FAM.getResult<LoopAnalysis>(F);
            ScalarEvolution &SE = FAM.getResult<ScalarEvolutionAnalysis>(F);
            if (!LI.empty()) {
                for (Loop *L : LI) {
                    analyzeLoop(L, SE, Out);
                }
            }
            Out << "=== End Function: " << F.getName() << " ===\n\n";
            Out.flush();

            return PreservedAnalyses::all();
        }

    private:
        // -------------------------------------------------------------------
        //   PART 1: CFG Analysis in a "Linearized" (BFS) Format
        // -------------------------------------------------------------------
        void analyzeFunctionCFG(Function &F, raw_fd_ostream &Out) {
            Out << "=== Linearized CFG for Function: " << F.getName() << " ===\n";
            if (F.empty()) {
                Out << "  (Function has no basic blocks)\n\n";
                return;
            }

            // Perform BFS from the entry block.
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
                for (const BasicBlock *Succ : successors(Curr)) {
                    if (!Visited.count(Succ)) {
                        Visited.insert(Succ);
                        Q.push(Succ);
                    }
                }
            }

            // Assign each block an index in BFS order and store in the member variable.
            FunctionBBIndexMap.clear();
            for (unsigned i = 0; i < BFSOrder.size(); i++) {
                FunctionBBIndexMap[BFSOrder[i]] = i;
            }

            // Gather block-level stats.
            struct BBStats {
                std::string Name;
                unsigned NumInsts = 0;
                unsigned NumLoads = 0;
                unsigned NumStores = 0;
                unsigned NumBranches = 0;
            };
            std::vector<BBStats> StatsVec(BFSOrder.size());
            for (unsigned i = 0; i < BFSOrder.size(); i++) {
                const BasicBlock *BB = BFSOrder[i];
                BBStats &S = StatsVec[i];
                // Use block name if present; otherwise, use its index.
                if (BB->hasName())
                    S.Name = BB->getName().str();
                else
                    S.Name = "bb_" + std::to_string(i);

                for (auto &Inst : *BB) {
                    S.NumInsts++;
                    if (isa<LoadInst>(Inst))
                        S.NumLoads++;
                    if (isa<StoreInst>(Inst))
                        S.NumStores++;
                    if (isa<BranchInst>(Inst))
                        S.NumBranches++;
                }
            }

            // Print the BFS-based linearization with block stats and successors.
            Out << "BFS Order (0-based indexing):\n";
            for (unsigned i = 0; i < BFSOrder.size(); i++) {
                const BasicBlock *BB = BFSOrder[i];
                const BBStats &S = StatsVec[i];
                Out << "  BlockIndex " << i << ": " << S.Name << "\n";
                Out << "    NumInsts=" << S.NumInsts
                    << " Loads=" << S.NumLoads
                    << " Stores=" << S.NumStores
                    << " Branches=" << S.NumBranches << "\n";
                Out << "    Successors=[";
                bool first = true;
                for (const BasicBlock *Succ : successors(BB)) {
                    if (FunctionBBIndexMap.find(Succ) != FunctionBBIndexMap.end()) {
                        if (!first)
                            Out << ", ";
                        Out << FunctionBBIndexMap[Succ];
                        first = false;
                    }
                }
                Out << "]\n";
            }
            Out << "=== End of Linearized CFG for " << F.getName() << " ===\n\n";
        }

        // -------------------------------------------------------------------
        //   PART 2: DFG Analysis (Def-Use Graph)
        // -------------------------------------------------------------------
        void analyzeDFG(Function &F, raw_fd_ostream &Out) {
            Out << "=== DFG Analysis for Function: " << F.getName() << " ===\n";
            std::unordered_map<const Instruction *, unsigned> InstToID;
            unsigned instCounter = 0;
            for (auto &BB : F) {
                for (auto &Inst : BB) {
                    InstToID[&Inst] = instCounter++;
                }
            }

            Out << "DFG Edges (source -> destination):\n";
            for (auto &BB : F) {
                for (auto &Inst : BB) {
                    unsigned dstID = InstToID[&Inst];
                    for (unsigned op = 0, n = Inst.getNumOperands(); op < n; op++) {
                        if (Instruction *srcInst = dyn_cast<Instruction>(Inst.getOperand(op))) {
                            if (InstToID.find(srcInst) != InstToID.end()) {
                                unsigned srcID = InstToID[srcInst];
                                Out << srcID << " -> " << dstID << "\n";
                            }
                        }
                    }
                }
            }
            Out << "=== End of DFG for " << F.getName() << " ===\n\n";
        }

        // -------------------------------------------------------------------
        //   PART 3: Loop Analysis (with Basic Block Listing by BFS Index)
        // -------------------------------------------------------------------
        static unsigned LoopCounter;

        void analyzeLoop(Loop *L, ScalarEvolution &SE, raw_fd_ostream &Out) {
            unsigned currentLoopID = LoopCounter++;
            BasicBlock *Header = L->getHeader();
            std::string HeaderStr = (Header && Header->hasName())
                                        ? Header->getName().str()
                                        : ("bb_" + std::to_string(FunctionBBIndexMap[Header]));

            unsigned NumInsts = 0;
            unsigned NumLoads = 0;
            unsigned NumStores = 0;
            unsigned NumBranches = 0;
            for (BasicBlock *BB : L->getBlocks()) {
                for (Instruction &I : *BB) {
                    NumInsts++;
                    if (isa<LoadInst>(I))
                        NumLoads++;
                    if (isa<StoreInst>(I))
                        NumStores++;
                    if (isa<BranchInst>(I))
                        NumBranches++;
                }
            }

            const SCEV *BackedgeCount = SE.getBackedgeTakenCount(L);
            std::optional<uint64_t> IterCount = std::nullopt;
            if (!isa<SCEVCouldNotCompute>(BackedgeCount)) {
                if (auto *C = dyn_cast<SCEVConstant>(BackedgeCount)) {
                    IterCount = C->getAPInt().getZExtValue() + 1;
                }
            }

            // Print loop info along with the list of basic block indices in the loop.
            Out << "=== Loop Analysis (ID: " << currentLoopID
                << ", Header: " << HeaderStr << ") ===\n";
            Out << "  Loop depth: " << L->getLoopDepth() << "\n";
            Out << "  NumBlocks: " << L->getNumBlocks() << "\n";
            Out << "  Basic blocks in loop: ";
            bool first = true;
            for (auto *BB : L->getBlocks()) {
                unsigned index = FunctionBBIndexMap[BB];
                if (!first)
                    Out << ", ";
                Out << index;
                first = false;
            }
            Out << "\n";
            Out << "  NumInstructions: " << NumInsts << "\n";
            Out << "    - Loads:  " << NumLoads << "\n";
            Out << "    - Stores: " << NumStores << "\n";
            Out << "    - Branches: " << NumBranches << "\n";
            if (IterCount.has_value())
                Out << "  Static Iteration Count: " << *IterCount << "\n";
            else
                Out << "  Iteration count: [Could not compute / symbolic]\n";
            Out << "\n";

            for (Loop *SubLoop : L->getSubLoops()) {
                analyzeLoop(SubLoop, SE, Out);
            }
        }
    };

    // Initialize static loop counter.
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
