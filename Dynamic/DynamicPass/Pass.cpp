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

#include "llvm/Analysis/AliasAnalysis.h"
#include "llvm/IR/Dominators.h"

#include <iostream>
#include <optional>
#include <queue> // for BFS queue
#include <set>   // to track visited blocks
#include <unordered_map>
#include <vector>

using namespace llvm;

namespace {

struct DynamicPass : public PassInfoMixin<DynamicPass> {

    PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
    std::error_code EC;
    raw_fd_ostream outFile("ml_features.txt", EC, sys::fs::OF_Text);
    
    if (EC) {
        outFile << "Error opening ml_features.txt: " << EC.message() << "\n";
        return PreservedAnalyses::all();
    }

    llvm::BlockFrequencyAnalysis::Result &bfi = FAM.getResult<BlockFrequencyAnalysis>(F);
    llvm::BranchProbabilityAnalysis::Result &bpi = FAM.getResult<BranchProbabilityAnalysis>(F);
    llvm::LoopAnalysis::Result &li = FAM.getResult<LoopAnalysis>(F);

    auto &dt = FAM.getResult<DominatorTreeAnalysis>(F);
    auto &AA = FAM.getResult<AAManager>(F);
    outFile << "=== Function: " << F.getName() << " ===\n";
    outFile << "========== Branch Counts ==========" << "\n";
    for (BasicBlock &BB : F) {
        BranchInst *BI = dyn_cast<BranchInst>(BB.getTerminator());
        if (!BI || BI->getNumSuccessors() == 0)
            continue;
        uint64_t BBFreq = bfi.getBlockFreq(&BB).getFrequency();
        BB.printAsOperand(outFile, false);
        outFile << ": " << BBFreq << "\n";
        /*
        for (unsigned i = 0; i < BI->getNumSuccessors(); ++i) {
            BasicBlock *Succ = BI->getSuccessor(i);
            BranchProbability Prob = bpi.getEdgeProbability(&BB, Succ);
            double edgeProb = static_cast<double>(Prob.getNumerator()) / Prob.getDenominator();
            uint64_t edgeCount = static_cast<uint64_t>(edgeProb * BBFreq);
            outFile << "  -> ";
            Succ->printAsOperand(outFile, false);
            outFile << ": " << edgeCount << "\n";
        }
        */
    }
    outFile << "\n=== Data Access Count ===\n";
    for (BasicBlock &BB : F) {
        uint64_t BBFreq = bfi.getBlockFreq(&BB).getFrequency();
        unsigned numInstr = BB.size();
        unsigned numLoads = 0;
        unsigned numStores = 0;

        for (Instruction &I : BB) {
            if (isa<LoadInst>(&I)) {
                numLoads++;
            } else if (isa<StoreInst>(&I)) {
                numStores++;
            }
        }
        uint64_t instrExecCount = numInstr * BBFreq;
        uint64_t loadExecCount = numLoads * BBFreq;
        uint64_t storeExecCount = numStores * BBFreq;
        BB.printAsOperand(outFile, false);
        outFile << ": executed " << BBFreq << " times\n";
        outFile << "  instr count: " << numInstr << " x " << BBFreq << " = " << instrExecCount << "\n";
        outFile << "  load count: " << numLoads << " x " << BBFreq << " = " << loadExecCount << "\n";
        outFile << "  store count: " << numStores << " x " << BBFreq << " = " << storeExecCount << "\n\n";
    }
    return PreservedAnalyses::all();
  }
};
}

extern "C" ::llvm::PassPluginLibraryInfo LLVM_ATTRIBUTE_WEAK llvmGetPassPluginInfo() {
  return {
    LLVM_PLUGIN_API_VERSION, "DynamicPass", "v0.1",
    [](PassBuilder &PB) {
      PB.registerPipelineParsingCallback(
        [](StringRef Name, FunctionPassManager &FPM,
        ArrayRef<PassBuilder::PipelineElement>) {
          if(Name == "dynamic-analysis"){
            FPM.addPass(DynamicPass());
            return true;
          }
          return false;
        }
      );
    }
  };
}