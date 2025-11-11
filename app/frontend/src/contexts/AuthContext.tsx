import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { authService } from "../services/auth.service";

interface User {
  id: string;
  email: string;
  name: string;
  role: "buyer" | "organizer";
}

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, name: string, role: "buyer" | "organizer") => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkSession();
  }, []);

  async function checkSession() {
    try {
      // Intentar recuperar sesión del localStorage
      const savedToken = localStorage.getItem("proticket_token");
      const savedUser = localStorage.getItem("proticket_user");

      if (savedToken && savedUser) {
        setAccessToken(savedToken);
        setUser(JSON.parse(savedUser));
      }
    } catch (error) {
      console.error("Error checking session:", error);
      localStorage.removeItem("proticket_token");
      localStorage.removeItem("proticket_user");
    } finally {
      setLoading(false);
    }
  }

  async function signIn(email: string, password: string) {
  try {
    const response = await authService.login({ email, password });
    
    setAccessToken(response.token);
    
    // Simular perfil de usuario basado en la respuesta
    setUser({
      id: response.userId,
      email: email,
      name: email.split('@')[0],
      role: response.role as "buyer" | "organizer",
    });
  } catch (error: any) {
    console.error("Sign in error:", error);
    throw new Error(error?.message || "Error al iniciar sesión");
  }
}

  async function signUp(email: string, password: string, name: string, role: "buyer" | "organizer") {
  try {
    const response = await authService.register({ 
      email, 
      password, 
      role 
    });
    
    // Auto login después del registro
    await signIn(email, password);
  } catch (error: any) {
    console.error("Sign up error:", error);
    throw error;
  }
}

  async function signOut() {
    try {
      setUser(null);
      setAccessToken(null);
      localStorage.removeItem("proticket_token");
      localStorage.removeItem("proticket_user");
      console.log("Signed out successfully");
    } catch (error) {
      console.error("Sign out error:", error);
      setUser(null);
      setAccessToken(null);
      localStorage.removeItem("proticket_token");
      localStorage.removeItem("proticket_user");
    }
  }

  return (
    <AuthContext.Provider value={{ user, accessToken, loading, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}