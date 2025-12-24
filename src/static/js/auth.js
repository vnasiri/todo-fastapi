/**
 * Authentication Module
 * Handles user authentication operations
 */

const auth = {
  /**
   * Register a new user
   */
  async register(username, email, password, first_name, last_name) {
    try {
      const data = await apiClient.post("/auth/register", {
        username,
        email,
        password,
        first_name,
        last_name,
      });

      return {
        success: true,
        data,
      };
    } catch (error) {
      throw new Error(error.message || "Registration failed");
    }
  },

  /**
   * Login user
   */
  async login(username, password) {
    try {
      // Use FormData for OAuth2PasswordRequestForm compatibility
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      const response = await fetch("/api/v1/auth/token", {
        method: "POST",
        credentials: "include",
        body: formData,
      });

      // Handle 401 Unauthorized
      if (response.status === 401) {
        throw new Error("Invalid username or password");
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Login failed");
      }

      const data = await response.json();

      return {
        success: true,
        data,
      };
    } catch (error) {
      throw new Error(error.message || "Login failed");
    }
  },

  /**
   * Logout user
   */
  async logout() {
    try {
      await apiClient.post("/auth/logout", {});
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      // Always redirect to login, cookie will be cleared by server
      window.location.href = "/login";
    }
  },

  /**
   * Verify email with token
   */
  async verifyEmail(token) {
    try {
      const data = await apiClient.get(
        `/auth/verify?token=${encodeURIComponent(token)}`
      );
      return {
        success: true,
        data,
      };
    } catch (error) {
      throw new Error(error.message || "Email verification failed");
    }
  },

  /**
   * Check if user is authenticated
   */
  async isAuthenticated() {
    try {
      await userAPI.getCurrentUser();
      return true;
    } catch (error) {
      return false;
    }
  },

  /**
   * Redirect to login if not authenticated
   */
  async requireAuth() {
    if (!(await this.isAuthenticated())) {
      window.location.href = "/login";
    }
  },
};