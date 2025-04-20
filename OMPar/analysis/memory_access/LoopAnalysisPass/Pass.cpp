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
        // Run the pass on a function using the new Pass Manager.
        // It obtains LoopInfo and instruments memory accesses inside loops.
        PreservedAnalyses run(Function &F, FunctionAnalysisManager &FAM) {
            // Get LoopInfo for the function.
            LoopInfo &LI = FAM.getResult<LoopAnalysis>(F);
            bool modified = false;
            LLVMContext &Ctx = F.getContext();
            Module *M = F.getParent();

            // Create an 8-bit integer pointer type: equivalent to void* parameter.
            Type *int8PtrTy = Type::getInt8Ty(Ctx)->getPointerTo();
            Type *int32Ty = Type::getInt32Ty(Ctx);

            // Option A: Use a vector (or ArrayRef) for parameter types.
            std::vector<Type *> paramTypes{int8PtrTy, int32Ty};
            FunctionType *logFuncTy = FunctionType::get(Type::getVoidTy(Ctx), paramTypes, false);
            FunctionCallee logFunc = M->getOrInsertFunction("logMemoryAccessFunc", logFuncTy);
            unsigned loopID = 0;
            // Iterate over each loop in the function.
            for (Loop *L : LI) {
                auto loopIdConstant = ConstantInt::get(int32Ty, loopID);

                // Process all blocks in the loop.
                for (BasicBlock *BB : L->getBlocks()) {
                    // Instrument each instruction in the basic block.
                    for (Instruction &I : *BB) {
                        if (auto *loadInst = dyn_cast<LoadInst>(&I)) {
                            IRBuilder<> Builder(loadInst);
                            Value *ptr = loadInst->getPointerOperand();
                            // Cast the pointer to i8* to match the logging function signature.
                            Value *castPtr = Builder.CreateBitCast(ptr, int8PtrTy);
                            Value *args[] = {castPtr, loopIdConstant};
                            Builder.CreateCall(logFunc, args);
                            modified = true;
                        } else if (auto *storeInst = dyn_cast<StoreInst>(&I)) {
                            IRBuilder<> Builder(storeInst);
                            Value *ptr = storeInst->getPointerOperand();
                            Value *castPtr = Builder.CreateBitCast(ptr, int8PtrTy);
                            Value *args[] = {castPtr, loopIdConstant};
                            Builder.CreateCall(logFunc, args);
                            modified = true;
                        }
                    }
                }
                loopID++;
                //     for (BasicBlock &BB : F) {
                //         for (Instruction &I : BB) {
                //             if (auto *loadInst = dyn_cast<LoadInst>(&I)) {
                //                 llvm::errs() << "Instrumenting load: " << *loadInst << "\n";
                //                 Value *ptr = loadInst->getPointerOperand();
                //                 llvm::errs() << "Original pointer: " << *ptr << "\n";
                //                 IRBuilder<> Builder(loadInst);
                //                 Value *castPtr = Builder.CreateBitCast(ptr, int8PtrTy);
                //                 llvm::errs() << "Cast pointer: " << *castPtr << "\n";
                //                 // Insert the call to logMemoryAccessFunc and print the result of insertion.
                //                 auto *callInst = cast<CallInst>(Builder.CreateCall(logFunc, castPtr));
                //                 llvm::errs() << "Inserted call: " << *callInst << "\n";
                //                 modified = true;
                //             } else if (auto *storeInst = dyn_cast<StoreInst>(&I)) {
                //                 llvm::errs() << "Instrumenting store: " << *storeInst << "\n";
                //                 Value *ptr = storeInst->getPointerOperand();
                //                 llvm::errs() << "Original pointer: " << *ptr << "\n";
                //                 IRBuilder<> Builder(storeInst);
                //                 Value *castPtr = Builder.CreateBitCast(ptr, int8PtrTy);
                //                 llvm::errs() << "Cast pointer: " << *castPtr << "\n";
                //                 auto *callInst = cast<CallInst>(Builder.CreateCall(logFunc, castPtr));
                //                 llvm::errs() << "Inserted call: " << *callInst << "\n";
                //                 modified = true;
                //             }
                //         }
                //     }
            }
            return modified ? PreservedAnalyses::none() : PreservedAnalyses::all();
        }
    };

} // end anonymous namespace

// Registration for the LLVM pass plugin.
llvm::PassPluginLibraryInfo
getLoopAnalysisPassPluginInfo() {
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
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return getLoopAnalysisPassPluginInfo();
}
