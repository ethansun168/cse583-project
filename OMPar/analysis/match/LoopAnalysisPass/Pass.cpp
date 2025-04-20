#include "llvm/Analysis/BlockFrequencyInfo.h"
#include "llvm/Analysis/BranchProbabilityInfo.h"
#include "llvm/Analysis/LoopAnalysisManager.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Analysis/ScalarEvolution.h"
#include "llvm/Analysis/ScalarEvolutionExpressions.h"
#include "llvm/IR/CFG.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/raw_ostream.h"

#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

using namespace llvm;

namespace {

// Global output file stream to write loop analysis results.
std::unique_ptr<raw_fd_ostream> LoopAnalysisOut;

// Helper function to read an entire source file into a vector of lines.
std::vector<std::string> getSourceFileLines(const std::string &Filename) {
  std::vector<std::string> Lines;
  std::ifstream File(Filename);
  if (!File.is_open())
    return Lines;
  std::string Line;
  while (std::getline(File, Line))
    Lines.push_back(Line);
  return Lines;
}

/// Given a filename and a starting line number (1-indexed), extract exactly 3 lines
/// in forward order—starting at the line pointed to by the debug location.
/// For example, if the debug location is line 10, it returns lines 10, 11, and 12.
std::string getThreeLoopLines(const std::string &Filename, unsigned StartLine) {
  std::vector<std::string> Lines = getSourceFileLines(Filename);
  if (Lines.empty())
    return "<source not available>";
  std::stringstream Snippet;
  // Adjust index because debug info is 1-indexed.
  unsigned startIdx = StartLine - 1;
  for (unsigned i = startIdx; i < std::min((unsigned)Lines.size(), startIdx + 3); ++i)
    Snippet << Lines[i] << "\n";
  return Snippet.str();
}

/// Recursively process a loop: extract three lines starting at the debug location
/// and write the output in the requested format.
void processLoop(Loop *L, int &loopCount) {
  BasicBlock *Header = L->getHeader();
  DebugLoc DL;
  // Obtain the first non-PHI instruction's debug location.
  for (Instruction &I : *Header) {
    if (!isa<PHINode>(I)) {
      DL = I.getDebugLoc();
      break;
    }
  }
  if (DL) {
    std::string Filename = DL->getFilename().str();
    unsigned Line = DL.getLine();
    std::string ThreeLines = getThreeLoopLines(Filename, Line);
    // Write in the format: "LoopID X, for { <3-lines snippet> }"
    *LoopAnalysisOut << "LoopID " << loopCount << ",  " << ThreeLines << " }\n";
    loopCount++;
  }
  // Process nested loops recursively.
  for (Loop *SubLoop : L->getSubLoops())
    processLoop(SubLoop, loopCount);
}

/// The LLVM pass that applies our loop analysis.
struct LoopAnalysisPass : public PassInfoMixin<LoopAnalysisPass> {
  PreservedAnalyses run(Function &F, FunctionAnalysisManager &AM) {
    // Open the output file if it hasn't been opened yet.
    if (!LoopAnalysisOut) {
      std::error_code EC;
      LoopAnalysisOut = std::make_unique<raw_fd_ostream>(
          "loop_analysis_output.txt", EC, sys::fs::OF_Text);
      if (EC)
        errs() << "Error opening loop_analysis_output.txt: " << EC.message() << "\n";
    }
    LoopInfo &LI = AM.getResult<LoopAnalysis>(F);
    int loopCount = 0;
    //for (Loop *L : LI)
      //processLoop(L, loopCount);
    for (auto it = LI.rbegin(); it != LI.rend(); ++it)
      processLoop(*it, loopCount);
    return PreservedAnalyses::all();
  }
};

} // end anonymous namespace

// Registration for the LLVM pass plugin.
llvm::PassPluginLibraryInfo getLoopAnalysisPassPluginInfo() {
  return {
      LLVM_PLUGIN_API_VERSION, "LoopAnalysisPass", "v0.1",
      [](PassBuilder &PB) {
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

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
  return getLoopAnalysisPassPluginInfo();
}