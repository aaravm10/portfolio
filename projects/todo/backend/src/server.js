const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const { fetchTodosFromCanvas } = require("./canvasService");

dotenv.config();

const app = express();
const port = process.env.PORT || 8080;

app.use(cors());
app.use(express.json());

app.get("/health", (_, res) => {
  res.json({ status: "ok" });
});

app.get("/api/todos", async (_, res) => {
  try {
    const todos = await fetchTodosFromCanvas();
    res.json(todos);
  } catch (error) {
    const statusCode = error.statusCode || 502;
    const message =
      error.response?.data?.message ||
      error.message ||
      "Failed to fetch Canvas assignments.";

    res.status(statusCode).json({
      error: message,
    });
  }
});

app.listen(port, () => {
  console.log(`Backend listening on port ${port}`);
});
