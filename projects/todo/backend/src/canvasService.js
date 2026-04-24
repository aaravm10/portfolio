const axios = require("axios");

const CANVAS_BASE_URL =
  process.env.CANVAS_BASE_URL || "https://canvas.instructure.com/api/v1";

function getAuthHeaders() {
  const token = process.env.CANVAS_API_KEY;

  if (!token) {
    const error = new Error("Missing CANVAS_API_KEY in environment.");
    error.statusCode = 500;
    throw error;
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}

async function fetchCourses() {
  const response = await axios.get(`${CANVAS_BASE_URL}/courses`, {
    headers: getAuthHeaders(),
    params: {
      enrollment_state: "active",
      per_page: 100,
    },
  });

  return response.data;
}

async function fetchAssignmentsForCourse(courseId) {
  const response = await axios.get(
    `${CANVAS_BASE_URL}/courses/${courseId}/assignments`,
    {
      headers: getAuthHeaders(),
      params: {
        per_page: 100,
      },
    },
  );

  return response.data;
}

function transformAssignments(courses, assignmentsByCourse) {
  const groupedByCourse = {};

  courses.forEach((course) => {
    const rawAssignments = assignmentsByCourse[course.id] || [];

    const todos = rawAssignments
      .filter((assignment) => assignment?.due_at)
      .map((assignment) => ({
        id: assignment.id,
        title: assignment.name,
        dueDate: assignment.due_at,
        courseName: course.name,
      }))
      .sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate));

    if (todos.length > 0) {
      groupedByCourse[course.name] = todos;
    }
  });

  const allTodos = Object.values(groupedByCourse)
    .flat()
    .sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate));

  return {
    groupedByCourse,
    allTodos,
  };
}

async function fetchTodosFromCanvas() {
  const courses = await fetchCourses();
  const assignmentEntries = await Promise.all(
    courses.map(async (course) => {
      const assignments = await fetchAssignmentsForCourse(course.id);
      return [course.id, assignments];
    }),
  );

  const assignmentsByCourse = Object.fromEntries(assignmentEntries);
  return transformAssignments(courses, assignmentsByCourse);
}

module.exports = {
  fetchTodosFromCanvas,
};
