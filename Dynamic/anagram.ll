; ModuleID = 'input/anagram.c'
source_filename = "input/anagram.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

%struct.Letter = type { i32, i32, i32, i32 }
%struct.__jmp_buf_tag = type { [8 x i64], i32, %struct.__sigset_t }
%struct.__sigset_t = type { [16 x i64] }
%struct.stat = type { i64, i64, i64, i32, i32, i32, i32, i64, i64, i64, i64, %struct.timespec, %struct.timespec, %struct.timespec, [3 x i64] }
%struct.timespec = type { i64, i64 }
%struct.Word = type { [2 x i64], ptr, i32 }

@cchMinLength = dso_local global i32 3, align 4
@stderr = external global ptr, align 8
@.str = private unnamed_addr constant [24 x i8] c"Cannot stat dictionary\0A\00", align 1
@pchDictionary = dso_local global ptr null, align 8
@.str.1 = private unnamed_addr constant [42 x i8] c"Unable to allocate memory for dictionary\0A\00", align 1
@.str.2 = private unnamed_addr constant [2 x i8] c"r\00", align 1
@.str.3 = private unnamed_addr constant [24 x i8] c"Cannot open dictionary\0A\00", align 1
@.str.4 = private unnamed_addr constant [32 x i8] c"main dictionary has %u entries\0A\00", align 1
@.str.5 = private unnamed_addr constant [41 x i8] c"Dictionary too large; increase MAXWORDS\0A\00", align 1
@.str.6 = private unnamed_addr constant [18 x i8] c"%lu bytes wasted\0A\00", align 1
@alPhrase = dso_local global [26 x %struct.Letter] zeroinitializer, align 16
@aqMainMask = dso_local global [2 x i64] zeroinitializer, align 16
@aqMainSign = dso_local global [2 x i64] zeroinitializer, align 16
@cchPhraseLength = dso_local global i32 0, align 4
@auGlobalFrequency = dso_local global [26 x i32] zeroinitializer, align 16
@.str.7 = private unnamed_addr constant [28 x i8] c"MAX_QUADS not large enough\0A\00", align 1
@.str.8 = private unnamed_addr constant [35 x i8] c"Out of memory after %d candidates\0A\00", align 1
@cpwCand = dso_local global i32 0, align 4
@.str.9 = private unnamed_addr constant [4 x i8] c"%s \00", align 1
@.str.10 = private unnamed_addr constant [21 x i8] c"Too many candidates\0A\00", align 1
@apwCand = dso_local global [5000 x ptr] zeroinitializer, align 16
@.str.11 = private unnamed_addr constant [15 x i8] c"%d candidates\0A\00", align 1
@.str.12 = private unnamed_addr constant [7 x i8] c"%15s%c\00", align 1
@.str.13 = private unnamed_addr constant [2 x i8] c"\0A\00", align 1
@DumpWords.X = internal global i32 0, align 4
@cpwLast = dso_local global i32 0, align 4
@apwSol = dso_local global [51 x ptr] zeroinitializer, align 16
@achByFrequency = dso_local global [26 x i8] zeroinitializer, align 16
@.str.14 = private unnamed_addr constant [25 x i8] c"Order of search will be \00", align 1
@fInteractive = dso_local global i32 0, align 4
@.str.15 = private unnamed_addr constant [2 x i8] c">\00", align 1
@stdout = external global ptr, align 8
@stdin = external global ptr, align 8
@.str.16 = private unnamed_addr constant [36 x i8] c"Usage: anagram dictionary [length]\0A\00", align 1
@achPhrase = dso_local global [255 x i8] zeroinitializer, align 16
@.str.17 = private unnamed_addr constant [16 x i8] c"New length: %d\0A\00", align 1
@jbAnagram = dso_local global [1 x %struct.__jmp_buf_tag] zeroinitializer, align 16

; Function Attrs: noinline nounwind uwtable
define dso_local void @Fatal(ptr noundef %0, i32 noundef %1) #0 {
  %3 = alloca ptr, align 8
  %4 = alloca i32, align 4
  store ptr %0, ptr %3, align 8
  store i32 %1, ptr %4, align 4
  %5 = load ptr, ptr @stderr, align 8
  %6 = load ptr, ptr %3, align 8
  %7 = load i32, ptr %4, align 4
  %8 = call i32 (ptr, ptr, ...) @fprintf(ptr noundef %5, ptr noundef %6, i32 noundef %7)
  call void @exit(i32 noundef 1) #9
  unreachable
}

declare i32 @fprintf(ptr noundef, ptr noundef, ...) #1

; Function Attrs: noreturn nounwind
declare void @exit(i32 noundef) #2

; Function Attrs: noinline nounwind uwtable
define dso_local void @ReadDict(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  %3 = alloca ptr, align 8
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  %6 = alloca i64, align 8
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  %9 = alloca i32, align 4
  %10 = alloca %struct.stat, align 8
  store ptr %0, ptr %2, align 8
  store i32 0, ptr %7, align 4
  %11 = load ptr, ptr %2, align 8
  %12 = call i32 @stat(ptr noundef %11, ptr noundef %10) #10
  %13 = icmp ne i32 %12, 0
  br i1 %13, label %14, label %15

14:                                               ; preds = %1
  call void @Fatal(ptr noundef @.str, i32 noundef 0)
  br label %15

15:                                               ; preds = %14, %1
  %16 = getelementptr inbounds %struct.stat, ptr %10, i32 0, i32 8
  %17 = load i64, ptr %16, align 8
  %18 = add i64 %17, 52000
  store i64 %18, ptr %6, align 8
  %19 = load i64, ptr %6, align 8
  %20 = call noalias ptr @malloc(i64 noundef %19) #11
  store ptr %20, ptr @pchDictionary, align 8
  store ptr %20, ptr %5, align 8
  %21 = load ptr, ptr @pchDictionary, align 8
  %22 = icmp eq ptr %21, null
  br i1 %22, label %23, label %24

23:                                               ; preds = %15
  call void @Fatal(ptr noundef @.str.1, i32 noundef 0)
  br label %24

24:                                               ; preds = %23, %15
  %25 = load ptr, ptr %2, align 8
  %26 = call noalias ptr @fopen(ptr noundef %25, ptr noundef @.str.2)
  store ptr %26, ptr %3, align 8
  %27 = icmp eq ptr %26, null
  br i1 %27, label %28, label %29

28:                                               ; preds = %24
  call void @Fatal(ptr noundef @.str.3, i32 noundef 0)
  br label %29

29:                                               ; preds = %28, %24
  br label %30

30:                                               ; preds = %65, %29
  %31 = load ptr, ptr %3, align 8
  %32 = call i32 @feof(ptr noundef %31) #10
  %33 = icmp ne i32 %32, 0
  %34 = xor i1 %33, true
  br i1 %34, label %35, label %82

35:                                               ; preds = %30
  %36 = load ptr, ptr %5, align 8
  %37 = getelementptr inbounds i8, ptr %36, i64 2
  store ptr %37, ptr %4, align 8
  store i32 0, ptr %8, align 4
  br label %38

38:                                               ; preds = %60, %35
  %39 = load ptr, ptr %3, align 8
  %40 = call i32 @fgetc(ptr noundef %39)
  store i32 %40, ptr %9, align 4
  %41 = icmp ne i32 %40, 10
  br i1 %41, label %42, label %45

42:                                               ; preds = %38
  %43 = load i32, ptr %9, align 4
  %44 = icmp ne i32 %43, -1
  br label %45

45:                                               ; preds = %42, %38
  %46 = phi i1 [ false, %38 ], [ %44, %42 ]
  br i1 %46, label %47, label %65

47:                                               ; preds = %45
  %48 = call ptr @__ctype_b_loc() #12
  %49 = load ptr, ptr %48, align 8
  %50 = load i32, ptr %9, align 4
  %51 = sext i32 %50 to i64
  %52 = getelementptr inbounds i16, ptr %49, i64 %51
  %53 = load i16, ptr %52, align 2
  %54 = zext i16 %53 to i32
  %55 = and i32 %54, 1024
  %56 = icmp ne i32 %55, 0
  br i1 %56, label %57, label %60

57:                                               ; preds = %47
  %58 = load i32, ptr %8, align 4
  %59 = add i32 %58, 1
  store i32 %59, ptr %8, align 4
  br label %60

60:                                               ; preds = %57, %47
  %61 = load i32, ptr %9, align 4
  %62 = trunc i32 %61 to i8
  %63 = load ptr, ptr %4, align 8
  %64 = getelementptr inbounds i8, ptr %63, i32 1
  store ptr %64, ptr %4, align 8
  store i8 %62, ptr %63, align 1
  br label %38, !llvm.loop !6

65:                                               ; preds = %45
  %66 = load ptr, ptr %4, align 8
  %67 = getelementptr inbounds i8, ptr %66, i32 1
  store ptr %67, ptr %4, align 8
  store i8 0, ptr %66, align 1
  %68 = load ptr, ptr %4, align 8
  %69 = load ptr, ptr %5, align 8
  %70 = ptrtoint ptr %68 to i64
  %71 = ptrtoint ptr %69 to i64
  %72 = sub i64 %70, %71
  %73 = trunc i64 %72 to i8
  %74 = load ptr, ptr %5, align 8
  store i8 %73, ptr %74, align 1
  %75 = load i32, ptr %8, align 4
  %76 = trunc i32 %75 to i8
  %77 = load ptr, ptr %5, align 8
  %78 = getelementptr inbounds i8, ptr %77, i64 1
  store i8 %76, ptr %78, align 1
  %79 = load ptr, ptr %4, align 8
  store ptr %79, ptr %5, align 8
  %80 = load i32, ptr %7, align 4
  %81 = add i32 %80, 1
  store i32 %81, ptr %7, align 4
  br label %30, !llvm.loop !8

82:                                               ; preds = %30
  %83 = load ptr, ptr %3, align 8
  %84 = call i32 @fclose(ptr noundef %83)
  %85 = load ptr, ptr %5, align 8
  %86 = getelementptr inbounds i8, ptr %85, i32 1
  store ptr %86, ptr %5, align 8
  store i8 0, ptr %85, align 1
  %87 = load ptr, ptr @stderr, align 8
  %88 = load i32, ptr %7, align 4
  %89 = call i32 (ptr, ptr, ...) @fprintf(ptr noundef %87, ptr noundef @.str.4, i32 noundef %88)
  %90 = load i32, ptr %7, align 4
  %91 = icmp uge i32 %90, 26000
  br i1 %91, label %92, label %93

92:                                               ; preds = %82
  call void @Fatal(ptr noundef @.str.5, i32 noundef 0)
  br label %93

93:                                               ; preds = %92, %82
  %94 = load ptr, ptr @stderr, align 8
  %95 = load i64, ptr %6, align 8
  %96 = load ptr, ptr %5, align 8
  %97 = load ptr, ptr @pchDictionary, align 8
  %98 = ptrtoint ptr %96 to i64
  %99 = ptrtoint ptr %97 to i64
  %100 = sub i64 %98, %99
  %101 = sub i64 %95, %100
  %102 = call i32 (ptr, ptr, ...) @fprintf(ptr noundef %94, ptr noundef @.str.6, i64 noundef %101)
  ret void
}

; Function Attrs: nounwind
declare i32 @stat(ptr noundef, ptr noundef) #3

; Function Attrs: nounwind allocsize(0)
declare noalias ptr @malloc(i64 noundef) #4

declare noalias ptr @fopen(ptr noundef, ptr noundef) #1

; Function Attrs: nounwind
declare i32 @feof(ptr noundef) #3

declare i32 @fgetc(ptr noundef) #1

; Function Attrs: nounwind willreturn memory(none)
declare ptr @__ctype_b_loc() #5

declare i32 @fclose(ptr noundef) #1

; Function Attrs: noinline nounwind uwtable
define dso_local void @BuildMask(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = alloca i32, align 4
  %6 = alloca i32, align 4
  %7 = alloca i32, align 4
  %8 = alloca i64, align 8
  store ptr %0, ptr %2, align 8
  call void @llvm.memset.p0.i64(ptr align 16 @alPhrase, i8 0, i64 416, i1 false)
  call void @llvm.memset.p0.i64(ptr align 16 @aqMainMask, i8 0, i64 16, i1 false)
  call void @llvm.memset.p0.i64(ptr align 16 @aqMainSign, i8 0, i64 16, i1 false)
  store i32 0, ptr @cchPhraseLength, align 4
  br label %9

9:                                                ; preds = %37, %1
  %10 = load ptr, ptr %2, align 8
  %11 = getelementptr inbounds i8, ptr %10, i32 1
  store ptr %11, ptr %2, align 8
  %12 = load i8, ptr %10, align 1
  %13 = sext i8 %12 to i32
  store i32 %13, ptr %4, align 4
  %14 = icmp ne i32 %13, 0
  br i1 %14, label %15, label %38

15:                                               ; preds = %9
  %16 = call ptr @__ctype_b_loc() #12
  %17 = load ptr, ptr %16, align 8
  %18 = load i32, ptr %4, align 4
  %19 = sext i32 %18 to i64
  %20 = getelementptr inbounds i16, ptr %17, i64 %19
  %21 = load i16, ptr %20, align 2
  %22 = zext i16 %21 to i32
  %23 = and i32 %22, 1024
  %24 = icmp ne i32 %23, 0
  br i1 %24, label %25, label %37

25:                                               ; preds = %15
  %26 = load i32, ptr %4, align 4
  %27 = call i32 @tolower(i32 noundef %26) #13
  store i32 %27, ptr %4, align 4
  %28 = load i32, ptr %4, align 4
  %29 = sub nsw i32 %28, 97
  %30 = sext i32 %29 to i64
  %31 = getelementptr inbounds [26 x %struct.Letter], ptr @alPhrase, i64 0, i64 %30
  %32 = getelementptr inbounds %struct.Letter, ptr %31, i32 0, i32 0
  %33 = load i32, ptr %32, align 16
  %34 = add i32 %33, 1
  store i32 %34, ptr %32, align 16
  %35 = load i32, ptr @cchPhraseLength, align 4
  %36 = add nsw i32 %35, 1
  store i32 %36, ptr @cchPhraseLength, align 4
  br label %37

37:                                               ; preds = %25, %15
  br label %9, !llvm.loop !9

38:                                               ; preds = %9
  store i32 0, ptr %5, align 4
  store i32 0, ptr %6, align 4
  store i32 0, ptr %3, align 4
  br label %39

39:                                               ; preds = %134, %38
  %40 = load i32, ptr %3, align 4
  %41 = icmp slt i32 %40, 26
  br i1 %41, label %42, label %137

42:                                               ; preds = %39
  %43 = load i32, ptr %3, align 4
  %44 = sext i32 %43 to i64
  %45 = getelementptr inbounds [26 x %struct.Letter], ptr @alPhrase, i64 0, i64 %44
  %46 = getelementptr inbounds %struct.Letter, ptr %45, i32 0, i32 0
  %47 = load i32, ptr %46, align 16
  %48 = icmp eq i32 %47, 0
  br i1 %48, label %49, label %53

49:                                               ; preds = %42
  %50 = load i32, ptr %3, align 4
  %51 = sext i32 %50 to i64
  %52 = getelementptr inbounds [26 x i32], ptr @auGlobalFrequency, i64 0, i64 %51
  store i32 -1, ptr %52, align 4
  br label %133

53:                                               ; preds = %42
  %54 = load i32, ptr %3, align 4
  %55 = sext i32 %54 to i64
  %56 = getelementptr inbounds [26 x i32], ptr @auGlobalFrequency, i64 0, i64 %55
  store i32 0, ptr %56, align 4
  store i32 1, ptr %7, align 4
  store i64 1, ptr %8, align 8
  br label %57

57:                                               ; preds = %67, %53
  %58 = load i32, ptr %3, align 4
  %59 = sext i32 %58 to i64
  %60 = getelementptr inbounds [26 x %struct.Letter], ptr @alPhrase, i64 0, i64 %59
  %61 = getelementptr inbounds %struct.Letter, ptr %60, i32 0, i32 0
  %62 = load i32, ptr %61, align 16
  %63 = zext i32 %62 to i64
  %64 = load i64, ptr %8, align 8
  %65 = icmp uge i64 %63, %64
  br i1 %65, label %66, label %72

66:                                               ; preds = %57
  br label %67

67:                                               ; preds = %66
  %68 = load i32, ptr %7, align 4
  %69 = add nsw i32 %68, 1
  store i32 %69, ptr %7, align 4
  %70 = load i64, ptr %8, align 8
  %71 = shl i64 %70, 1
  store i64 %71, ptr %8, align 8
  br label %57, !llvm.loop !10

72:                                               ; preds = %57
  %73 = load i32, ptr %6, align 4
  %74 = load i32, ptr %7, align 4
  %75 = add nsw i32 %73, %74
  %76 = sext i32 %75 to i64
  %77 = icmp ugt i64 %76, 64
  br i1 %77, label %78, label %84

78:                                               ; preds = %72
  %79 = load i32, ptr %5, align 4
  %80 = add i32 %79, 1
  store i32 %80, ptr %5, align 4
  %81 = icmp uge i32 %80, 2
  br i1 %81, label %82, label %83

82:                                               ; preds = %78
  call void @Fatal(ptr noundef @.str.7, i32 noundef 0)
  br label %83

83:                                               ; preds = %82, %78
  store i32 0, ptr %6, align 4
  br label %84

84:                                               ; preds = %83, %72
  %85 = load i64, ptr %8, align 8
  %86 = sub i64 %85, 1
  %87 = trunc i64 %86 to i32
  %88 = load i32, ptr %3, align 4
  %89 = sext i32 %88 to i64
  %90 = getelementptr inbounds [26 x %struct.Letter], ptr @alPhrase, i64 0, i64 %89
  %91 = getelementptr inbounds %struct.Letter, ptr %90, i32 0, i32 2
  store i32 %87, ptr %91, align 8
  %92 = load i32, ptr %6, align 4
  %93 = icmp ne i32 %92, 0
  br i1 %93, label %94, label %99

94:                                               ; preds = %84
  %95 = load i32, ptr %6, align 4
  %96 = load i64, ptr %8, align 8
  %97 = zext i32 %95 to i64
  %98 = shl i64 %96, %97
  store i64 %98, ptr %8, align 8
  br label %99

99:                                               ; preds = %94, %84
  %100 = load i64, ptr %8, align 8
  %101 = load i32, ptr %5, align 4
  %102 = zext i32 %101 to i64
  %103 = getelementptr inbounds [2 x i64], ptr @aqMainSign, i64 0, i64 %102
  %104 = load i64, ptr %103, align 8
  %105 = or i64 %104, %100
  store i64 %105, ptr %103, align 8
  %106 = load i32, ptr %3, align 4
  %107 = sext i32 %106 to i64
  %108 = getelementptr inbounds [26 x %struct.Letter], ptr @alPhrase, i64 0, i64 %107
  %109 = getelementptr inbounds %struct.Letter, ptr %108, i32 0, i32 0
  %110 = load i32, ptr %109, align 16
  %111 = zext i32 %110 to i64
  %112 = load i32, ptr %6, align 4
  %113 = zext i32 %112 to i64
  %114 = shl i64 %111, %113
  %115 = load i32, ptr %5, align 4
  %116 = zext i32 %115 to i64
  %117 = getelementptr inbounds [2 x i64], ptr @aqMainMask, i64 0, i64 %116
  %118 = load i64, ptr %117, align 8
  %119 = or i64 %118, %114
  store i64 %119, ptr %117, align 8
  %120 = load i32, ptr %6, align 4
  %121 = load i32, ptr %3, align 4
  %122 = sext i32 %121 to i64
  %123 = getelementptr inbounds [26 x %struct.Letter], ptr @alPhrase, i64 0, i64 %122
  %124 = getelementptr inbounds %struct.Letter, ptr %123, i32 0, i32 1
  store i32 %120, ptr %124, align 4
  %125 = load i32, ptr %5, align 4
  %126 = load i32, ptr %3, align 4
  %127 = sext i32 %126 to i64
  %128 = getelementptr inbounds [26 x %struct.Letter], ptr @alPhrase, i64 0, i64 %127
  %129 = getelementptr inbounds %struct.Letter, ptr %128, i32 0, i32 3
  store i32 %125, ptr %129, align 4
  %130 = load i32, ptr %7, align 4
  %131 = load i32, ptr %6, align 4
  %132 = add nsw i32 %131, %130
  store i32 %132, ptr %6, align 4
  br label %133

133:                                              ; preds = %99, %49
  br label %134

134:                                              ; preds = %133
  %135 = load i32, ptr %3, align 4
  %136 = add nsw i32 %135, 1
  store i32 %136, ptr %3, align 4
  br label %39, !llvm.loop !11

137:                                              ; preds = %39
  ret void
}

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr nocapture writeonly, i8, i64, i1 immarg) #6

; Function Attrs: nounwind willreturn memory(read)
declare i32 @tolower(i32 noundef) #7

; Function Attrs: noinline nounwind uwtable
define dso_local ptr @NewWord() #0 {
  %1 = alloca ptr, align 8
  %2 = call noalias ptr @malloc(i64 noundef 32) #11
  store ptr %2, ptr %1, align 8
  %3 = load ptr, ptr %1, align 8
  %4 = icmp eq ptr %3, null
  br i1 %4, label %5, label %7

5:                                                ; preds = %0
  %6 = load i32, ptr @cpwCand, align 4
  call void @Fatal(ptr noundef @.str.8, i32 noundef %6)
  br label %7

7:                                                ; preds = %5, %0
  %8 = load ptr, ptr %1, align 8
  ret ptr %8
}

; Function Attrs: noinline nounwind uwtable
define dso_local void @wprint(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  %3 = load ptr, ptr %2, align 8
  %4 = call i32 (ptr, ...) @printf(ptr noundef @.str.9, ptr noundef %3)
  ret void
}

declare i32 @printf(ptr noundef, ...) #1

; Function Attrs: noinline nounwind uwtable
define dso_local ptr @NextWord() #0 {
  %1 = alloca ptr, align 8
  %2 = alloca ptr, align 8
  %3 = load i32, ptr @cpwCand, align 4
  %4 = icmp uge i32 %3, 5000
  br i1 %4, label %5, label %6

5:                                                ; preds = %0
  call void @Fatal(ptr noundef @.str.10, i32 noundef 0)
  br label %6

6:                                                ; preds = %5, %0
  %7 = load i32, ptr @cpwCand, align 4
  %8 = add i32 %7, 1
  store i32 %8, ptr @cpwCand, align 4
  %9 = zext i32 %7 to i64
  %10 = getelementptr inbounds [5000 x ptr], ptr @apwCand, i64 0, i64 %9
  %11 = load ptr, ptr %10, align 8
  store ptr %11, ptr %2, align 8
  %12 = load ptr, ptr %2, align 8
  %13 = icmp ne ptr %12, null
  br i1 %13, label %14, label %16

14:                                               ; preds = %6
  %15 = load ptr, ptr %2, align 8
  store ptr %15, ptr %1, align 8
  br label %27

16:                                               ; preds = %6
  %17 = call ptr @NewWord()
  %18 = load i32, ptr @cpwCand, align 4
  %19 = sub i32 %18, 1
  %20 = zext i32 %19 to i64
  %21 = getelementptr inbounds [5000 x ptr], ptr @apwCand, i64 0, i64 %20
  store ptr %17, ptr %21, align 8
  %22 = load i32, ptr @cpwCand, align 4
  %23 = sub i32 %22, 1
  %24 = zext i32 %23 to i64
  %25 = getelementptr inbounds [5000 x ptr], ptr @apwCand, i64 0, i64 %24
  %26 = load ptr, ptr %25, align 8
  store ptr %26, ptr %1, align 8
  br label %27

27:                                               ; preds = %16, %14
  %28 = load ptr, ptr %1, align 8
  ret ptr %28
}

; Function Attrs: noinline nounwind uwtable
define dso_local void @BuildWord(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  %3 = alloca [26 x i8], align 16
  %4 = alloca i32, align 4
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  %7 = alloca i32, align 4
  store ptr %0, ptr %2, align 8
  %8 = load ptr, ptr %2, align 8
  store ptr %8, ptr %5, align 8
  store i32 0, ptr %7, align 4
  %9 = getelementptr inbounds [26 x i8], ptr %3, i64 0, i64 0
  call void @llvm.memset.p0.i64(ptr align 16 %9, i8 0, i64 26, i1 false)
  br label %10

10:                                               ; preds = %44, %26, %1
  %11 = load ptr, ptr %5, align 8
  %12 = getelementptr inbounds i8, ptr %11, i32 1
  store ptr %12, ptr %5, align 8
  %13 = load i8, ptr %11, align 1
  %14 = sext i8 %13 to i32
  store i32 %14, ptr %4, align 4
  %15 = icmp ne i32 %14, 0
  br i1 %15, label %16, label %47

16:                                               ; preds = %10
  %17 = call ptr @__ctype_b_loc() #12
  %18 = load ptr, ptr %17, align 8
  %19 = load i32, ptr %4, align 4
  %20 = sext i32 %19 to i64
  %21 = getelementptr inbounds i16, ptr %18, i64 %20
  %22 = load i16, ptr %21, align 2
  %23 = zext i16 %22 to i32
  %24 = and i32 %23, 1024
  %25 = icmp ne i32 %24, 0
  br i1 %25, label %27, label %26

26:                                               ; preds = %16
  br label %10, !llvm.loop !12

27:                                               ; preds = %16
  %28 = load i32, ptr %4, align 4
  %29 = call i32 @tolower(i32 noundef %28) #13
  %30 = sub nsw i32 %29, 97
  store i32 %30, ptr %4, align 4
  %31 = load i32, ptr %4, align 4
  %32 = sext i32 %31 to i64
  %33 = getelementptr inbounds [26 x i8], ptr %3, i64 0, i64 %32
  %34 = load i8, ptr %33, align 1
  %35 = add i8 %34, 1
  store i8 %35, ptr %33, align 1
  %36 = zext i8 %35 to i32
  %37 = load i32, ptr %4, align 4
  %38 = sext i32 %37 to i64
  %39 = getelementptr inbounds [26 x %struct.Letter], ptr @alPhrase, i64 0, i64 %38
  %40 = getelementptr inbounds %struct.Letter, ptr %39, i32 0, i32 0
  %41 = load i32, ptr %40, align 16
  %42 = icmp ugt i32 %36, %41
  br i1 %42, label %43, label %44

43:                                               ; preds = %27
  br label %106

44:                                               ; preds = %27
  %45 = load i32, ptr %7, align 4
  %46 = add nsw i32 %45, 1
  store i32 %46, ptr %7, align 4
  br label %10, !llvm.loop !12

47:                                               ; preds = %10
  store i32 0, ptr %4, align 4
  br label %48

48:                                               ; preds = %62, %47
  %49 = load i32, ptr %4, align 4
  %50 = icmp slt i32 %49, 26
  br i1 %50, label %51, label %65

51:                                               ; preds = %48
  %52 = load i32, ptr %4, align 4
  %53 = sext i32 %52 to i64
  %54 = getelementptr inbounds [26 x i8], ptr %3, i64 0, i64 %53
  %55 = load i8, ptr %54, align 1
  %56 = zext i8 %55 to i32
  %57 = load i32, ptr %4, align 4
  %58 = sext i32 %57 to i64
  %59 = getelementptr inbounds [26 x i32], ptr @auGlobalFrequency, i64 0, i64 %58
  %60 = load i32, ptr %59, align 4
  %61 = add i32 %60, %56
  store i32 %61, ptr %59, align 4
  br label %62

62:                                               ; preds = %51
  %63 = load i32, ptr %4, align 4
  %64 = add nsw i32 %63, 1
  store i32 %64, ptr %4, align 4
  br label %48, !llvm.loop !13

65:                                               ; preds = %48
  %66 = call ptr @NextWord()
  store ptr %66, ptr %6, align 8
  %67 = load ptr, ptr %6, align 8
  %68 = getelementptr inbounds %struct.Word, ptr %67, i32 0, i32 0
  %69 = getelementptr inbounds [2 x i64], ptr %68, i64 0, i64 0
  call void @llvm.memset.p0.i64(ptr align 8 %69, i8 0, i64 16, i1 false)
  %70 = load ptr, ptr %2, align 8
  %71 = load ptr, ptr %6, align 8
  %72 = getelementptr inbounds %struct.Word, ptr %71, i32 0, i32 1
  store ptr %70, ptr %72, align 8
  %73 = load i32, ptr %7, align 4
  %74 = load ptr, ptr %6, align 8
  %75 = getelementptr inbounds %struct.Word, ptr %74, i32 0, i32 2
  store i32 %73, ptr %75, align 8
  store i32 0, ptr %4, align 4
  br label %76

76:                                               ; preds = %103, %65
  %77 = load i32, ptr %4, align 4
  %78 = icmp slt i32 %77, 26
  br i1 %78, label %79, label %106

79:                                               ; preds = %76
  %80 = load i32, ptr %4, align 4
  %81 = sext i32 %80 to i64
  %82 = getelementptr inbounds [26 x i8], ptr %3, i64 0, i64 %81
  %83 = load i8, ptr %82, align 1
  %84 = zext i8 %83 to i64
  %85 = load i32, ptr %4, align 4
  %86 = sext i32 %85 to i64
  %87 = getelementptr inbounds [26 x %struct.Letter], ptr @alPhrase, i64 0, i64 %86
  %88 = getelementptr inbounds %struct.Letter, ptr %87, i32 0, i32 1
  %89 = load i32, ptr %88, align 4
  %90 = zext i32 %89 to i64
  %91 = shl i64 %84, %90
  %92 = load ptr, ptr %6, align 8
  %93 = getelementptr inbounds %struct.Word, ptr %92, i32 0, i32 0
  %94 = load i32, ptr %4, align 4
  %95 = sext i32 %94 to i64
  %96 = getelementptr inbounds [26 x %struct.Letter], ptr @alPhrase, i64 0, i64 %95
  %97 = getelementptr inbounds %struct.Letter, ptr %96, i32 0, i32 3
  %98 = load i32, ptr %97, align 4
  %99 = zext i32 %98 to i64
  %100 = getelementptr inbounds [2 x i64], ptr %93, i64 0, i64 %99
  %101 = load i64, ptr %100, align 8
  %102 = or i64 %101, %91
  store i64 %102, ptr %100, align 8
  br label %103

103:                                              ; preds = %79
  %104 = load i32, ptr %4, align 4
  %105 = add nsw i32 %104, 1
  store i32 %105, ptr %4, align 4
  br label %76, !llvm.loop !14

106:                                              ; preds = %43, %76
  ret void
}

; Function Attrs: noinline nounwind uwtable
define dso_local void @AddWords() #0 {
  %1 = alloca ptr, align 8
  %2 = load ptr, ptr @pchDictionary, align 8
  store ptr %2, ptr %1, align 8
  store i32 0, ptr @cpwCand, align 4
  br label %3

3:                                                ; preds = %33, %0
  %4 = load ptr, ptr %1, align 8
  %5 = load i8, ptr %4, align 1
  %6 = icmp ne i8 %5, 0
  br i1 %6, label %7, label %40

7:                                                ; preds = %3
  %8 = load ptr, ptr %1, align 8
  %9 = getelementptr inbounds i8, ptr %8, i64 1
  %10 = load i8, ptr %9, align 1
  %11 = sext i8 %10 to i32
  %12 = load i32, ptr @cchMinLength, align 4
  %13 = icmp sge i32 %11, %12
  br i1 %13, label %14, label %23

14:                                               ; preds = %7
  %15 = load ptr, ptr %1, align 8
  %16 = getelementptr inbounds i8, ptr %15, i64 1
  %17 = load i8, ptr %16, align 1
  %18 = sext i8 %17 to i32
  %19 = load i32, ptr @cchMinLength, align 4
  %20 = add nsw i32 %18, %19
  %21 = load i32, ptr @cchPhraseLength, align 4
  %22 = icmp sle i32 %20, %21
  br i1 %22, label %30, label %23

23:                                               ; preds = %14, %7
  %24 = load ptr, ptr %1, align 8
  %25 = getelementptr inbounds i8, ptr %24, i64 1
  %26 = load i8, ptr %25, align 1
  %27 = sext i8 %26 to i32
  %28 = load i32, ptr @cchPhraseLength, align 4
  %29 = icmp eq i32 %27, %28
  br i1 %29, label %30, label %33

30:                                               ; preds = %23, %14
  %31 = load ptr, ptr %1, align 8
  %32 = getelementptr inbounds i8, ptr %31, i64 2
  call void @BuildWord(ptr noundef %32)
  br label %33

33:                                               ; preds = %30, %23
  %34 = load ptr, ptr %1, align 8
  %35 = load i8, ptr %34, align 1
  %36 = sext i8 %35 to i32
  %37 = load ptr, ptr %1, align 8
  %38 = sext i32 %36 to i64
  %39 = getelementptr inbounds i8, ptr %37, i64 %38
  store ptr %39, ptr %1, align 8
  br label %3, !llvm.loop !15

40:                                               ; preds = %3
  %41 = load ptr, ptr @stderr, align 8
  %42 = load i32, ptr @cpwCand, align 4
  %43 = call i32 (ptr, ptr, ...) @fprintf(ptr noundef %41, ptr noundef @.str.11, i32 noundef %42)
  ret void
}

; Function Attrs: noinline nounwind uwtable
define dso_local void @DumpCandidates() #0 {
  %1 = alloca i32, align 4
  store i32 0, ptr %1, align 4
  br label %2

2:                                                ; preds = %19, %0
  %3 = load i32, ptr %1, align 4
  %4 = load i32, ptr @cpwCand, align 4
  %5 = icmp ult i32 %3, %4
  br i1 %5, label %6, label %22

6:                                                ; preds = %2
  %7 = load i32, ptr %1, align 4
  %8 = zext i32 %7 to i64
  %9 = getelementptr inbounds [5000 x ptr], ptr @apwCand, i64 0, i64 %8
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds %struct.Word, ptr %10, i32 0, i32 1
  %12 = load ptr, ptr %11, align 8
  %13 = load i32, ptr %1, align 4
  %14 = urem i32 %13, 4
  %15 = icmp eq i32 %14, 3
  %16 = zext i1 %15 to i64
  %17 = select i1 %15, i32 10, i32 32
  %18 = call i32 (ptr, ...) @printf(ptr noundef @.str.12, ptr noundef %12, i32 noundef %17)
  br label %19

19:                                               ; preds = %6
  %20 = load i32, ptr %1, align 4
  %21 = add i32 %20, 1
  store i32 %21, ptr %1, align 4
  br label %2, !llvm.loop !16

22:                                               ; preds = %2
  %23 = call i32 (ptr, ...) @printf(ptr noundef @.str.13)
  ret void
}

; Function Attrs: noinline nounwind uwtable
define dso_local void @DumpWords() #0 {
  %1 = alloca i32, align 4
  %2 = load i32, ptr @DumpWords.X, align 4
  %3 = add nsw i32 %2, 1
  %4 = and i32 %3, 1023
  store i32 %4, ptr @DumpWords.X, align 4
  %5 = load i32, ptr @DumpWords.X, align 4
  %6 = icmp ne i32 %5, 0
  br i1 %6, label %7, label %8

7:                                                ; preds = %0
  br label %25

8:                                                ; preds = %0
  store i32 0, ptr %1, align 4
  br label %9

9:                                                ; preds = %20, %8
  %10 = load i32, ptr %1, align 4
  %11 = load i32, ptr @cpwLast, align 4
  %12 = icmp slt i32 %10, %11
  br i1 %12, label %13, label %23

13:                                               ; preds = %9
  %14 = load i32, ptr %1, align 4
  %15 = sext i32 %14 to i64
  %16 = getelementptr inbounds [51 x ptr], ptr @apwSol, i64 0, i64 %15
  %17 = load ptr, ptr %16, align 8
  %18 = getelementptr inbounds %struct.Word, ptr %17, i32 0, i32 1
  %19 = load ptr, ptr %18, align 8
  call void @wprint(ptr noundef %19)
  br label %20

20:                                               ; preds = %13
  %21 = load i32, ptr %1, align 4
  %22 = add nsw i32 %21, 1
  store i32 %22, ptr %1, align 4
  br label %9, !llvm.loop !17

23:                                               ; preds = %9
  %24 = call i32 (ptr, ...) @printf(ptr noundef @.str.13)
  br label %25

25:                                               ; preds = %23, %7
  ret void
}

; Function Attrs: noinline nounwind uwtable
define dso_local void @FindAnagram(ptr noundef %0, ptr noundef %1, i32 noundef %2) #0 {
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  %6 = alloca i32, align 4
  %7 = alloca [2 x i64], align 16
  %8 = alloca ptr, align 8
  %9 = alloca i64, align 8
  %10 = alloca i32, align 4
  %11 = alloca ptr, align 8
  store ptr %0, ptr %4, align 8
  store ptr %1, ptr %5, align 8
  store i32 %2, ptr %6, align 4
  store ptr @apwCand, ptr %11, align 8
  %12 = load i32, ptr @cpwCand, align 4
  %13 = load ptr, ptr %11, align 8
  %14 = zext i32 %12 to i64
  %15 = getelementptr inbounds ptr, ptr %13, i64 %14
  store ptr %15, ptr %11, align 8
  br label %16

16:                                               ; preds = %52, %3
  %17 = load i32, ptr %6, align 4
  %18 = sext i32 %17 to i64
  %19 = getelementptr inbounds [26 x i8], ptr @achByFrequency, i64 0, i64 %18
  %20 = load i8, ptr %19, align 1
  %21 = sext i8 %20 to i64
  %22 = getelementptr inbounds [26 x %struct.Letter], ptr @alPhrase, i64 0, i64 %21
  %23 = getelementptr inbounds %struct.Letter, ptr %22, i32 0, i32 3
  %24 = load i32, ptr %23, align 4
  store i32 %24, ptr %10, align 4
  %25 = load i32, ptr %6, align 4
  %26 = sext i32 %25 to i64
  %27 = getelementptr inbounds [26 x i8], ptr @achByFrequency, i64 0, i64 %26
  %28 = load i8, ptr %27, align 1
  %29 = sext i8 %28 to i64
  %30 = getelementptr inbounds [26 x %struct.Letter], ptr @alPhrase, i64 0, i64 %29
  %31 = getelementptr inbounds %struct.Letter, ptr %30, i32 0, i32 2
  %32 = load i32, ptr %31, align 8
  %33 = load i32, ptr %6, align 4
  %34 = sext i32 %33 to i64
  %35 = getelementptr inbounds [26 x i8], ptr @achByFrequency, i64 0, i64 %34
  %36 = load i8, ptr %35, align 1
  %37 = sext i8 %36 to i64
  %38 = getelementptr inbounds [26 x %struct.Letter], ptr @alPhrase, i64 0, i64 %37
  %39 = getelementptr inbounds %struct.Letter, ptr %38, i32 0, i32 1
  %40 = load i32, ptr %39, align 4
  %41 = shl i32 %32, %40
  %42 = zext i32 %41 to i64
  store i64 %42, ptr %9, align 8
  %43 = load ptr, ptr %4, align 8
  %44 = load i32, ptr %10, align 4
  %45 = zext i32 %44 to i64
  %46 = getelementptr inbounds i64, ptr %43, i64 %45
  %47 = load i64, ptr %46, align 8
  %48 = load i64, ptr %9, align 8
  %49 = and i64 %47, %48
  %50 = icmp ne i64 %49, 0
  br i1 %50, label %51, label %52

51:                                               ; preds = %16
  br label %55

52:                                               ; preds = %16
  %53 = load i32, ptr %6, align 4
  %54 = add nsw i32 %53, 1
  store i32 %54, ptr %6, align 4
  br label %16

55:                                               ; preds = %51
  br label %56

56:                                               ; preds = %132, %104, %91, %75, %55
  %57 = load ptr, ptr %5, align 8
  %58 = load ptr, ptr %11, align 8
  %59 = icmp ult ptr %57, %58
  br i1 %59, label %60, label %142

60:                                               ; preds = %56
  %61 = load ptr, ptr %5, align 8
  %62 = load ptr, ptr %61, align 8
  store ptr %62, ptr %8, align 8
  %63 = load ptr, ptr %4, align 8
  %64 = getelementptr inbounds i64, ptr %63, i64 0
  %65 = load i64, ptr %64, align 8
  %66 = load ptr, ptr %8, align 8
  %67 = getelementptr inbounds %struct.Word, ptr %66, i32 0, i32 0
  %68 = getelementptr inbounds [2 x i64], ptr %67, i64 0, i64 0
  %69 = load i64, ptr %68, align 8
  %70 = sub i64 %65, %69
  %71 = getelementptr inbounds [2 x i64], ptr %7, i64 0, i64 0
  store i64 %70, ptr %71, align 16
  %72 = load i64, ptr @aqMainSign, align 16
  %73 = and i64 %70, %72
  %74 = icmp ne i64 %73, 0
  br i1 %74, label %75, label %78

75:                                               ; preds = %60
  %76 = load ptr, ptr %5, align 8
  %77 = getelementptr inbounds ptr, ptr %76, i32 1
  store ptr %77, ptr %5, align 8
  br label %56, !llvm.loop !18

78:                                               ; preds = %60
  %79 = load ptr, ptr %4, align 8
  %80 = getelementptr inbounds i64, ptr %79, i64 1
  %81 = load i64, ptr %80, align 8
  %82 = load ptr, ptr %8, align 8
  %83 = getelementptr inbounds %struct.Word, ptr %82, i32 0, i32 0
  %84 = getelementptr inbounds [2 x i64], ptr %83, i64 0, i64 1
  %85 = load i64, ptr %84, align 8
  %86 = sub i64 %81, %85
  %87 = getelementptr inbounds [2 x i64], ptr %7, i64 0, i64 1
  store i64 %86, ptr %87, align 8
  %88 = load i64, ptr getelementptr inbounds ([2 x i64], ptr @aqMainSign, i64 0, i64 1), align 8
  %89 = and i64 %86, %88
  %90 = icmp ne i64 %89, 0
  br i1 %90, label %91, label %94

91:                                               ; preds = %78
  %92 = load ptr, ptr %5, align 8
  %93 = getelementptr inbounds ptr, ptr %92, i32 1
  store ptr %93, ptr %5, align 8
  br label %56, !llvm.loop !18

94:                                               ; preds = %78
  %95 = load ptr, ptr %8, align 8
  %96 = getelementptr inbounds %struct.Word, ptr %95, i32 0, i32 0
  %97 = load i32, ptr %10, align 4
  %98 = zext i32 %97 to i64
  %99 = getelementptr inbounds [2 x i64], ptr %96, i64 0, i64 %98
  %100 = load i64, ptr %99, align 8
  %101 = load i64, ptr %9, align 8
  %102 = and i64 %100, %101
  %103 = icmp eq i64 %102, 0
  br i1 %103, label %104, label %111

104:                                              ; preds = %94
  %105 = load ptr, ptr %11, align 8
  %106 = getelementptr inbounds ptr, ptr %105, i32 -1
  store ptr %106, ptr %11, align 8
  %107 = load ptr, ptr %106, align 8
  %108 = load ptr, ptr %5, align 8
  store ptr %107, ptr %108, align 8
  %109 = load ptr, ptr %8, align 8
  %110 = load ptr, ptr %11, align 8
  store ptr %109, ptr %110, align 8
  br label %56, !llvm.loop !18

111:                                              ; preds = %94
  %112 = load ptr, ptr %8, align 8
  %113 = load i32, ptr @cpwLast, align 4
  %114 = add nsw i32 %113, 1
  store i32 %114, ptr @cpwLast, align 4
  %115 = sext i32 %113 to i64
  %116 = getelementptr inbounds [51 x ptr], ptr @apwSol, i64 0, i64 %115
  store ptr %112, ptr %116, align 8
  %117 = load ptr, ptr %8, align 8
  %118 = getelementptr inbounds %struct.Word, ptr %117, i32 0, i32 2
  %119 = load i32, ptr %118, align 8
  %120 = load i32, ptr @cchPhraseLength, align 4
  %121 = sub i32 %120, %119
  store i32 %121, ptr @cchPhraseLength, align 4
  %122 = icmp ne i32 %121, 0
  br i1 %122, label %123, label %131

123:                                              ; preds = %111
  store ptr @apwCand, ptr %11, align 8
  %124 = load i32, ptr @cpwCand, align 4
  %125 = load ptr, ptr %11, align 8
  %126 = zext i32 %124 to i64
  %127 = getelementptr inbounds ptr, ptr %125, i64 %126
  store ptr %127, ptr %11, align 8
  %128 = getelementptr inbounds [2 x i64], ptr %7, i64 0, i64 0
  %129 = load ptr, ptr %5, align 8
  %130 = load i32, ptr %6, align 4
  call void @FindAnagram(ptr noundef %128, ptr noundef %129, i32 noundef %130)
  br label %132

131:                                              ; preds = %111
  call void @DumpWords()
  br label %132

132:                                              ; preds = %131, %123
  %133 = load ptr, ptr %8, align 8
  %134 = getelementptr inbounds %struct.Word, ptr %133, i32 0, i32 2
  %135 = load i32, ptr %134, align 8
  %136 = load i32, ptr @cchPhraseLength, align 4
  %137 = add i32 %136, %135
  store i32 %137, ptr @cchPhraseLength, align 4
  %138 = load i32, ptr @cpwLast, align 4
  %139 = add nsw i32 %138, -1
  store i32 %139, ptr @cpwLast, align 4
  %140 = load ptr, ptr %5, align 8
  %141 = getelementptr inbounds ptr, ptr %140, i32 1
  store ptr %141, ptr %5, align 8
  br label %56, !llvm.loop !18

142:                                              ; preds = %56
  ret void
}

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @CompareFrequency(ptr noundef %0, ptr noundef %1) #0 {
  %3 = alloca i32, align 4
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  store ptr %0, ptr %4, align 8
  store ptr %1, ptr %5, align 8
  %6 = load ptr, ptr %4, align 8
  %7 = load i8, ptr %6, align 1
  %8 = sext i8 %7 to i64
  %9 = getelementptr inbounds [26 x i32], ptr @auGlobalFrequency, i64 0, i64 %8
  %10 = load i32, ptr %9, align 4
  %11 = load ptr, ptr %5, align 8
  %12 = load i8, ptr %11, align 1
  %13 = sext i8 %12 to i64
  %14 = getelementptr inbounds [26 x i32], ptr @auGlobalFrequency, i64 0, i64 %13
  %15 = load i32, ptr %14, align 4
  %16 = icmp ult i32 %10, %15
  br i1 %16, label %17, label %18

17:                                               ; preds = %2
  store i32 -1, ptr %3, align 4
  br label %50

18:                                               ; preds = %2
  %19 = load ptr, ptr %4, align 8
  %20 = load i8, ptr %19, align 1
  %21 = sext i8 %20 to i64
  %22 = getelementptr inbounds [26 x i32], ptr @auGlobalFrequency, i64 0, i64 %21
  %23 = load i32, ptr %22, align 4
  %24 = load ptr, ptr %5, align 8
  %25 = load i8, ptr %24, align 1
  %26 = sext i8 %25 to i64
  %27 = getelementptr inbounds [26 x i32], ptr @auGlobalFrequency, i64 0, i64 %26
  %28 = load i32, ptr %27, align 4
  %29 = icmp ugt i32 %23, %28
  br i1 %29, label %30, label %31

30:                                               ; preds = %18
  store i32 1, ptr %3, align 4
  br label %50

31:                                               ; preds = %18
  %32 = load ptr, ptr %4, align 8
  %33 = load i8, ptr %32, align 1
  %34 = sext i8 %33 to i32
  %35 = load ptr, ptr %5, align 8
  %36 = load i8, ptr %35, align 1
  %37 = sext i8 %36 to i32
  %38 = icmp slt i32 %34, %37
  br i1 %38, label %39, label %40

39:                                               ; preds = %31
  store i32 -1, ptr %3, align 4
  br label %50

40:                                               ; preds = %31
  %41 = load ptr, ptr %4, align 8
  %42 = load i8, ptr %41, align 1
  %43 = sext i8 %42 to i32
  %44 = load ptr, ptr %5, align 8
  %45 = load i8, ptr %44, align 1
  %46 = sext i8 %45 to i32
  %47 = icmp sgt i32 %43, %46
  br i1 %47, label %48, label %49

48:                                               ; preds = %40
  store i32 1, ptr %3, align 4
  br label %50

49:                                               ; preds = %40
  store i32 0, ptr %3, align 4
  br label %50

50:                                               ; preds = %49, %48, %39, %30, %17
  %51 = load i32, ptr %3, align 4
  ret i32 %51
}

; Function Attrs: noinline nounwind uwtable
define dso_local void @SortCandidates() #0 {
  %1 = alloca i32, align 4
  store i32 0, ptr %1, align 4
  br label %2

2:                                                ; preds = %11, %0
  %3 = load i32, ptr %1, align 4
  %4 = icmp slt i32 %3, 26
  br i1 %4, label %5, label %14

5:                                                ; preds = %2
  %6 = load i32, ptr %1, align 4
  %7 = trunc i32 %6 to i8
  %8 = load i32, ptr %1, align 4
  %9 = sext i32 %8 to i64
  %10 = getelementptr inbounds [26 x i8], ptr @achByFrequency, i64 0, i64 %9
  store i8 %7, ptr %10, align 1
  br label %11

11:                                               ; preds = %5
  %12 = load i32, ptr %1, align 4
  %13 = add nsw i32 %12, 1
  store i32 %13, ptr %1, align 4
  br label %2, !llvm.loop !19

14:                                               ; preds = %2
  call void @qsort(ptr noundef @achByFrequency, i64 noundef 26, i64 noundef 1, ptr noundef @CompareFrequency)
  %15 = load ptr, ptr @stderr, align 8
  %16 = call i32 (ptr, ptr, ...) @fprintf(ptr noundef %15, ptr noundef @.str.14)
  store i32 0, ptr %1, align 4
  br label %17

17:                                               ; preds = %29, %14
  %18 = load i32, ptr %1, align 4
  %19 = icmp slt i32 %18, 26
  br i1 %19, label %20, label %32

20:                                               ; preds = %17
  %21 = load i32, ptr %1, align 4
  %22 = sext i32 %21 to i64
  %23 = getelementptr inbounds [26 x i8], ptr @achByFrequency, i64 0, i64 %22
  %24 = load i8, ptr %23, align 1
  %25 = sext i8 %24 to i32
  %26 = add nsw i32 %25, 97
  %27 = load ptr, ptr @stderr, align 8
  %28 = call i32 @fputc(i32 noundef %26, ptr noundef %27)
  br label %29

29:                                               ; preds = %20
  %30 = load i32, ptr %1, align 4
  %31 = add nsw i32 %30, 1
  store i32 %31, ptr %1, align 4
  br label %17, !llvm.loop !20

32:                                               ; preds = %17
  %33 = load ptr, ptr @stderr, align 8
  %34 = call i32 @fputc(i32 noundef 10, ptr noundef %33)
  ret void
}

declare void @qsort(ptr noundef, i64 noundef, i64 noundef, ptr noundef) #1

declare i32 @fputc(i32 noundef, ptr noundef) #1

; Function Attrs: noinline nounwind uwtable
define dso_local ptr @GetPhrase(ptr noundef %0, i32 noundef %1) #0 {
  %3 = alloca ptr, align 8
  %4 = alloca i32, align 4
  store ptr %0, ptr %3, align 8
  store i32 %1, ptr %4, align 4
  %5 = load i32, ptr @fInteractive, align 4
  %6 = icmp ne i32 %5, 0
  br i1 %6, label %7, label %9

7:                                                ; preds = %2
  %8 = call i32 (ptr, ...) @printf(ptr noundef @.str.15)
  br label %9

9:                                                ; preds = %7, %2
  %10 = load ptr, ptr @stdout, align 8
  %11 = call i32 @fflush(ptr noundef %10)
  %12 = load ptr, ptr %3, align 8
  %13 = load i32, ptr %4, align 4
  %14 = load ptr, ptr @stdin, align 8
  %15 = call ptr @fgets(ptr noundef %12, i32 noundef %13, ptr noundef %14)
  %16 = icmp eq ptr %15, null
  br i1 %16, label %17, label %18

17:                                               ; preds = %9
  call void @exit(i32 noundef 0) #9
  unreachable

18:                                               ; preds = %9
  %19 = load ptr, ptr %3, align 8
  ret ptr %19
}

declare i32 @fflush(ptr noundef) #1

declare ptr @fgets(ptr noundef, i32 noundef, ptr noundef) #1

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @main(i32 noundef %0, ptr noundef %1) #0 {
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = alloca ptr, align 8
  store i32 0, ptr %3, align 4
  store i32 %0, ptr %4, align 4
  store ptr %1, ptr %5, align 8
  %6 = load i32, ptr %4, align 4
  %7 = icmp ne i32 %6, 2
  br i1 %7, label %8, label %12

8:                                                ; preds = %2
  %9 = load i32, ptr %4, align 4
  %10 = icmp ne i32 %9, 3
  br i1 %10, label %11, label %12

11:                                               ; preds = %8
  call void @Fatal(ptr noundef @.str.16, i32 noundef 0)
  br label %12

12:                                               ; preds = %11, %8, %2
  %13 = load i32, ptr %4, align 4
  %14 = icmp eq i32 %13, 3
  br i1 %14, label %15, label %20

15:                                               ; preds = %12
  %16 = load ptr, ptr %5, align 8
  %17 = getelementptr inbounds ptr, ptr %16, i64 2
  %18 = load ptr, ptr %17, align 8
  %19 = call i32 @atoi(ptr noundef %18) #13
  store i32 %19, ptr @cchMinLength, align 4
  br label %20

20:                                               ; preds = %15, %12
  %21 = call i32 @isatty(i32 noundef 1) #10
  store i32 %21, ptr @fInteractive, align 4
  %22 = load ptr, ptr %5, align 8
  %23 = getelementptr inbounds ptr, ptr %22, i64 1
  %24 = load ptr, ptr %23, align 8
  call void @ReadDict(ptr noundef %24)
  br label %25

25:                                               ; preds = %61, %54, %20
  %26 = call ptr @GetPhrase(ptr noundef @achPhrase, i32 noundef 255)
  %27 = icmp ne ptr %26, null
  br i1 %27, label %28, label %62

28:                                               ; preds = %25
  %29 = call ptr @__ctype_b_loc() #12
  %30 = load ptr, ptr %29, align 8
  %31 = load i8, ptr @achPhrase, align 16
  %32 = sext i8 %31 to i32
  %33 = sext i32 %32 to i64
  %34 = getelementptr inbounds i16, ptr %30, i64 %33
  %35 = load i16, ptr %34, align 2
  %36 = zext i16 %35 to i32
  %37 = and i32 %36, 2048
  %38 = icmp ne i32 %37, 0
  br i1 %38, label %39, label %43

39:                                               ; preds = %28
  %40 = call i32 @atoi(ptr noundef @achPhrase) #13
  store i32 %40, ptr @cchMinLength, align 4
  %41 = load i32, ptr @cchMinLength, align 4
  %42 = call i32 (ptr, ...) @printf(ptr noundef @.str.17, i32 noundef %41)
  br label %61

43:                                               ; preds = %28
  %44 = load i8, ptr @achPhrase, align 16
  %45 = sext i8 %44 to i32
  %46 = icmp eq i32 %45, 63
  br i1 %46, label %47, label %48

47:                                               ; preds = %43
  call void @DumpCandidates()
  br label %60

48:                                               ; preds = %43
  call void @BuildMask(ptr noundef @achPhrase)
  call void @AddWords()
  %49 = load i32, ptr @cpwCand, align 4
  %50 = icmp eq i32 %49, 0
  br i1 %50, label %54, label %51

51:                                               ; preds = %48
  %52 = load i32, ptr @cchPhraseLength, align 4
  %53 = icmp eq i32 %52, 0
  br i1 %53, label %54, label %55

54:                                               ; preds = %51, %48
  br label %25, !llvm.loop !21

55:                                               ; preds = %51
  store i32 0, ptr @cpwLast, align 4
  call void @SortCandidates()
  %56 = call i32 @_setjmp(ptr noundef @jbAnagram) #14
  %57 = icmp eq i32 %56, 0
  br i1 %57, label %58, label %59

58:                                               ; preds = %55
  call void @FindAnagram(ptr noundef @aqMainMask, ptr noundef @apwCand, i32 noundef 0)
  br label %59

59:                                               ; preds = %58, %55
  br label %60

60:                                               ; preds = %59, %47
  br label %61

61:                                               ; preds = %60, %39
  br label %25, !llvm.loop !21

62:                                               ; preds = %25
  ret i32 0
}

; Function Attrs: nounwind willreturn memory(read)
declare i32 @atoi(ptr noundef) #7

; Function Attrs: nounwind
declare i32 @isatty(i32 noundef) #3

; Function Attrs: nounwind returns_twice
declare i32 @_setjmp(ptr noundef) #8

attributes #0 = { noinline nounwind uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #2 = { noreturn nounwind "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { nounwind "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nounwind allocsize(0) "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { nounwind willreturn memory(none) "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #6 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #7 = { nounwind willreturn memory(read) "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #8 = { nounwind returns_twice "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #9 = { noreturn nounwind }
attributes #10 = { nounwind }
attributes #11 = { nounwind allocsize(0) }
attributes #12 = { nounwind willreturn memory(none) }
attributes #13 = { nounwind willreturn memory(read) }
attributes #14 = { nounwind returns_twice }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"clang version 18.1.8 (https://github.com/llvm/llvm-project.git 3b5b5c1ec4a3095ab096dd780e84d7ab81f3d7ff)"}
!6 = distinct !{!6, !7}
!7 = !{!"llvm.loop.mustprogress"}
!8 = distinct !{!8, !7}
!9 = distinct !{!9, !7}
!10 = distinct !{!10, !7}
!11 = distinct !{!11, !7}
!12 = distinct !{!12, !7}
!13 = distinct !{!13, !7}
!14 = distinct !{!14, !7}
!15 = distinct !{!15, !7}
!16 = distinct !{!16, !7}
!17 = distinct !{!17, !7}
!18 = distinct !{!18, !7}
!19 = distinct !{!19, !7}
!20 = distinct !{!20, !7}
!21 = distinct !{!21, !7}
