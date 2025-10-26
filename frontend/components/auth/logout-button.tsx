"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { logout } from "@/lib/auth";
import { useAuthStore } from "@/stores/auth-store";
import { Alert } from "@/components/ui/alert";
import { useState } from "react";

export function LogoutButton() {
  const [showError, setShowError] = useState<string | null>(null);
  const token = useAuthStore((state) => state.token);
  const clearAuth = useAuthStore((state) => state.clearAuth);
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async () => {
      if (!token) {
        throw new Error("No token available");
      }
      return logout(token);
    },
    onSuccess: () => {
      clearAuth();
      queryClient.clear();
    },
    onError: (error) => {
      setShowError(error instanceof Error ? error.message : "Failed to logout");
    },
  });

  return (
    <div className="flex flex-col items-end gap-2">
      {showError && <Alert variant="destructive">{showError}</Alert>}
      <Button
        variant="outline"
        size="sm"
        onClick={() => {
          setShowError(null);
          mutation.mutate();
        }}
        disabled={mutation.isPending}
      >
        {mutation.isPending ? "Logging out..." : "Log out"}
      </Button>
    </div>
  );
}

