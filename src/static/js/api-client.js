/**
 * API Client Module
 * Handles all HTTP requests to the backend API
 */

const apiClient = {
  baseURL: "/api/v1",

  /**
   * Generic fetch wrapper with error handling
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const defaultHeaders = {
      "Content-Type": "application/json",
    };

    const config = {
      credentials: "include", // Always include cookies
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      // Handle 401 Unauthorized - redirect to login
      if (response.status === 401) {
        window.location.href = "/login";
        return null;
      }

      // Handle 422 Unprocessable Entity - validation error
      if (response.status === 422) {
        const errorData = await response.json();
        console.error("Validation Error Details:", errorData);

        // Extract error message from FastAPI validation errors
        let errorMsg = "Validation error";
        if (errorData.detail && Array.isArray(errorData.detail)) {
          const errors = errorData.detail.map((err) => {
            const field = err.loc && err.loc.length > 1 ? err.loc[1] : "field";
            return `${field}: ${err.msg}`;
          });
          errorMsg = errors.join(", ");
        } else if (errorData.detail && typeof errorData.detail === "string") {
          errorMsg = errorData.detail;
        }
        throw new Error(errorMsg);
      }

      // Handle 403 Forbidden
      if (response.status === 403) {
        throw new Error("You do not have permission to access this resource.");
      }

      // Handle 404 Not Found
      if (response.status === 404) {
        throw new Error("The requested resource was not found.");
      }

      // Handle server errors
      if (response.status >= 500) {
        throw new Error("Server error. Please try again later.");
      }

      // Return null for 204 No Content
      if (response.status === 204) {
        return null;
      }

      // Parse response
      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      // Check if response is successful
      if (!response.ok) {
        const errorMsg =
          typeof data.detail === "string"
            ? data.detail
            : typeof data.detail === "object"
            ? JSON.stringify(data.detail)
            : data.message || "An error occurred";
        throw new Error(errorMsg);
      }

      return data;
    } catch (error) {
      console.error("API Error:", error);
      throw error;
    }
  },

  /**
   * GET request
   */
  get(endpoint, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "GET",
    });
  },

  /**
   * POST request
   */
  post(endpoint, data = {}, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  /**
   * PUT request
   */
  put(endpoint, data = {}, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  /**
   * PATCH request
   */
  patch(endpoint, data = {}, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  /**
   * DELETE request
   */
  delete(endpoint, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "DELETE",
    });
  },
};

/**
 * Todo API Client
 */
const todoAPI = {
  /**
   * Create a new todo
   */
  async createTodo(data) {
    return apiClient.post("/todos", data);
  },

  /**
   * Get all todos for the current user
   */
  async getTodos(offset = 0, limit = 10) {
    return apiClient.get(`/todos?offset=${offset}&limit=${limit}`);
  },

  /**
   * Get a specific todo by ID
   */
  async getTodo(id) {
    return apiClient.get(`/todos/${id}`);
  },

  /**
   * Update a todo
   */
  async updateTodo(id, data) {
    return apiClient.put(`/todos/${id}`, data);
  },

  /**
   * Partially update a todo
   */
  async patchTodo(id, data) {
    return apiClient.patch(`/todos/${id}`, data);
  },

  /**
   * Delete a todo
   */
  async deleteTodo(id) {
    return apiClient.delete(`/todos/${id}`);
  },
};

/**
 * User API Client
 */
const userAPI = {
  /**
   * Get current user profile
   */
  async getCurrentUser() {
    return apiClient.get("/users/me");
  },

  /**
   * Update user profile
   */
  async updateProfile(data) {
    return apiClient.put("/users/me", data);
  },

  /**
   * Change user password
   */
  async changePassword(data) {
    return apiClient.post("/users/change-password", data);
  },

  /**
   * Get user by ID
   */
  async getUser(id) {
    return apiClient.get(`/users/${id}`);
  },
};
