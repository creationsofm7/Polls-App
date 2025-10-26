"use client";

import { useState } from "react";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { AuthForm } from "./forms";

export function AuthDialog() {
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [open, setOpen] = useState(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">Sign in</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {mode === "signin" ? "Sign in to your account" : "Create a new account"}
          </DialogTitle>
          <DialogDescription>
            {mode === "signin"
              ? "Enter your credentials to access your polls."
              : "Fill the form below to get started."}
          </DialogDescription>
        </DialogHeader>

        <AuthForm
          mode={mode}
          onSuccess={() => {
            if (mode === "signin") {
              setOpen(false);
            } else {
              setMode("signin");
            }
          }}
        />

        <div className="text-sm text-center text-muted-foreground">
          {mode === "signin" ? (
            <button className="underline" onClick={() => setMode("signup")}>
              Need an account? Sign up
            </button>
          ) : (
            <button className="underline" onClick={() => setMode("signin")}>
              Already registered? Sign in
            </button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

