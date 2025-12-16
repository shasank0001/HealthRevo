import { useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { Heart } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function Login() {
  const { login } = useAuth();
  const { toast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"patient" | "doctor">("patient");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(email, password);
      toast({
        title: "Login successful",
        description: `Welcome back!`,
      });
    } catch (error) {
      console.error("Login error:", error);
      toast({
        title: "Login failed",
        description: "Invalid email or password. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardContent className="p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
              <Heart className="w-8 h-8 text-primary-foreground" />
            </div>
            <h1 className="text-3xl font-bold text-foreground mb-2">HealthRevo</h1>
            <p className="text-muted-foreground">AI-Powered Healthcare Platform</p>
          </div>

          <form onSubmit={handleSubmit} data-testid="form-login">
            <div className="space-y-4">
              <div>
                <Label htmlFor="email" className="block text-sm font-medium text-foreground mb-2">
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="doctor@healthai.com"
                  required
                  data-testid="input-email"
                />
              </div>
              
              <div>
                <Label htmlFor="password" className="block text-sm font-medium text-foreground mb-2">
                  Password
                </Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  data-testid="input-password"
                />
              </div>
              
              <div>
                <Label htmlFor="role" className="block text-sm font-medium text-foreground mb-2">
                  Role
                </Label>
                <Select value={role} onValueChange={(value: "patient" | "doctor") => setRole(value)}>
                  <SelectTrigger data-testid="select-role">
                    <SelectValue placeholder="Select your role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="patient">Patient</SelectItem>
                    <SelectItem value="doctor">Doctor</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full mt-6"
              disabled={isLoading}
              data-testid="button-sign-in"
            >
              {isLoading ? "Signing in..." : "Sign In"}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground mb-4">
              Demo Accounts
            </p>
            <div className="space-y-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => {
                  setEmail("john.doe@email.com");
                  setPassword("patient123");
                  setRole("patient");
                }}
              >
                Use Patient Demo Account
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => {
                  setEmail("doctor@healthrevo.com");
                  setPassword("doctor123");
                  setRole("doctor");
                }}
              >
                Use Doctor Demo Account
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-4">
              Patient: john.doe@email.com<br />
              Doctor: doctor@healthrevo.com<br />
              Password: patient123 / doctor123
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
