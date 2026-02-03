import { Router } from "express";
import jwt from "jsonwebtoken";
import bcrypt from "bcryptjs";
import { body, validationResult } from "express-validator";
import { PrismaClient } from "@prisma/client";
import dotenv from "dotenv"

const prisma = new PrismaClient();
const authRoutes = Router();
dotenv.config()

authRoutes.post(
  "/register",
  [
    body("email").isEmail().normalizeEmail(),
    body("username").isLength({ min: 3 }),
    body("password")
      .isLength({ min: 5 })
      .withMessage("Password must be at least 5 characters long"),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { email, username, password } = req.body;

    try {
      const existingUser = await prisma.user.findFirst({where: {OR: [{ email }, { username }]},});
      if (existingUser) {
        return res
          .status(409)
          .json({ message: "Email or username already exists" });
      }

      const hashedPassword = await bcrypt.hash(password, 10);

      const newUser = await prisma.user.create({
        data: {
          email,
          username,
          passwordHash: hashedPassword,
        },
      });

      if(!process.env.JWT_SECRET) {
        throw new Error("Secret Token is not defined")
      }

      const token = jwt.sign(
        { userId: newUser.id },
        process.env.JWT_SECRET,
        { expiresIn: "24h" }
      );

      return res.status(201).json({
        message: "User has been created",
        token,
      });
    } catch (error) {
      console.error(error);
      return res.status(500).json({ message: "Internal server error" });
    }
  }
);


authRoutes.post(
  "/login",
  [
    body("username").trim().isLength({ min: 3 }),
    body("password")
      .trim()
      .isLength({ min: 5 })
      .withMessage("Password must be at least 5 characters long"),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { username, password } = req.body;

    try {
      const existingUser = await prisma.user.findUnique({
        where: { username },
      });

      if (!existingUser) {
        return res.status(401).json({ message: "Invalid credentials" });
      }

      const passwordMatch = await bcrypt.compare(
        password,
        existingUser.passwordHash
      );

      if (!passwordMatch) {
        return res.status(401).json({ message: "Invalid credentials" });
      }

      if (!process.env.JWT_SECRET) {
        throw new Error("JWT_SECRET is not defined");
      }

      const token = jwt.sign(
        { userId: existingUser.id },
        process.env.JWT_SECRET,
        { expiresIn: "24h" }
      );

      return res.status(200).json({
        message: "User has been logged in",
        token,
      });
    } catch (error) {
      console.error(error);
      return res.status(500).json({ message: "Internal server error" });
    }
  }
);


export default authRoutes;
