-- CreateEnum
CREATE TYPE "GameType" AS ENUM ('SONGLESS', 'MOVIELESS', 'GAMELESS', 'CUSTOM');

-- CreateTable
CREATE TABLE "User" (
    "id" SERIAL NOT NULL,
    "username" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "passwordHash" TEXT NOT NULL,
    "streak" INTEGER NOT NULL DEFAULT 0,
    "longestStreak" INTEGER NOT NULL DEFAULT 0,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Game" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "type" "GameType" NOT NULL,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Game_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "DailyPuzzle" (
    "id" SERIAL NOT NULL,
    "gameId" INTEGER NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,
    "answer" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "DailyPuzzle_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "GameResult" (
    "id" SERIAL NOT NULL,
    "userId" INTEGER NOT NULL,
    "puzzleId" INTEGER NOT NULL,
    "guesses" INTEGER NOT NULL,
    "completed" BOOLEAN NOT NULL,
    "timeTaken" INTEGER NOT NULL,
    "score" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "GameResult_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Guess" (
    "id" SERIAL NOT NULL,
    "gameResultId" INTEGER NOT NULL,
    "guess" TEXT NOT NULL,
    "isCorrect" BOOLEAN NOT NULL,
    "guessNumber" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Guess_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "LeaderboardSnapshot" (
    "id" SERIAL NOT NULL,
    "gameId" INTEGER NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "LeaderboardSnapshot_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_username_key" ON "User"("username");

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE UNIQUE INDEX "Game_name_key" ON "Game"("name");

-- CreateIndex
CREATE UNIQUE INDEX "Game_slug_key" ON "Game"("slug");

-- CreateIndex
CREATE INDEX "DailyPuzzle_date_idx" ON "DailyPuzzle"("date");

-- CreateIndex
CREATE UNIQUE INDEX "DailyPuzzle_gameId_date_key" ON "DailyPuzzle"("gameId", "date");

-- CreateIndex
CREATE INDEX "GameResult_userId_idx" ON "GameResult"("userId");

-- CreateIndex
CREATE INDEX "GameResult_puzzleId_idx" ON "GameResult"("puzzleId");

-- CreateIndex
CREATE UNIQUE INDEX "GameResult_userId_puzzleId_key" ON "GameResult"("userId", "puzzleId");

-- CreateIndex
CREATE INDEX "Guess_gameResultId_idx" ON "Guess"("gameResultId");

-- AddForeignKey
ALTER TABLE "DailyPuzzle" ADD CONSTRAINT "DailyPuzzle_gameId_fkey" FOREIGN KEY ("gameId") REFERENCES "Game"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GameResult" ADD CONSTRAINT "GameResult_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GameResult" ADD CONSTRAINT "GameResult_puzzleId_fkey" FOREIGN KEY ("puzzleId") REFERENCES "DailyPuzzle"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Guess" ADD CONSTRAINT "Guess_gameResultId_fkey" FOREIGN KEY ("gameResultId") REFERENCES "GameResult"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
