"use client";

import { useForm, type FieldErrors } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";

import { Field, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { login, signup } from "@/lib/auth";
import { useAuthStore } from "@/stores/auth-store";
import { APIError } from "@/lib/api-client";

const signupSchema = z
  .object({
    full_name: z.string().optional(),
    email: z.email("Enter a valid email address"),
    password: z.string().min(6, "Password must be at least 6 characters"),
    confirm_password: z.string().min(6, "Re-type your password"),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

const loginSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

type SignupValues = z.infer<typeof signupSchema>;
type LoginValues = z.infer<typeof loginSchema>;

interface AuthFormProps {
  mode: "signup" | "signin";
  onSuccess?: () => void;
}

export function AuthForm({ mode, onSuccess }: AuthFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<SignupValues | LoginValues>({
    resolver: zodResolver(mode === "signup" ? signupSchema : loginSchema),
  });

  const setAuth = useAuthStore((state) => state.setAuthData);

  const signupErrors = errors as FieldErrors<SignupValues>;

  const mutation = useMutation({
    mutationFn: async (values: SignupValues | LoginValues) => {
      if (mode === "signup") {
        const { email, password, full_name } = values as SignupValues;
        const user = await signup({ email, password, full_name });
        return { user };
      }
      return login(values as LoginValues);
    },
    onSuccess: (data) => {
      if ("access_token" in data) {
        setAuth({
          token: data.access_token,
          expiresIn: data.expires_in,
          user: data.user,
        });
      }
      reset();
      onSuccess?.();
    },
  });

  const onSubmit = (values: SignupValues | LoginValues) => {
    mutation.mutate(values);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <FieldGroup>
        {mode === "signup" && (
          <Field>
            <FieldLabel htmlFor="full_name">Full name</FieldLabel>
            <Input id="full_name" placeholder="Jane Doe" {...register("full_name")} />
            <FieldError>{mode === "signup" ? signupErrors.full_name?.message : undefined}</FieldError>
          </Field>
        )}

        <Field>
          <FieldLabel htmlFor="email">Email</FieldLabel>
          <Input
            id="email"
            type="email"
            placeholder="you@example.com"
            autoComplete="email"
            {...register("email")}
          />
          <FieldError>{errors.email?.message}</FieldError>
        </Field>

        <Field>
          <FieldLabel htmlFor="password">Password</FieldLabel>
          <Input
            id="password"
            type="password"
            placeholder="••••••••"
            autoComplete={mode === "signup" ? "new-password" : "current-password"}
            {...register("password")}
          />
          <FieldError>{errors.password?.message}</FieldError>
        </Field>

        {mode === "signup" && (
          <Field>
            <FieldLabel htmlFor="confirm_password">Confirm password</FieldLabel>
            <Input
              id="confirm_password"
              type="password"
              placeholder="••••••••"
              autoComplete="new-password"
              {...register("confirm_password")}
            />
            <FieldError>
              {mode === "signup" ? signupErrors.confirm_password?.message : undefined}
            </FieldError>
          </Field>
        )}
      </FieldGroup>

      {mutation.isError && (
        <Alert variant="destructive">
          {mutation.error instanceof APIError
            ? typeof mutation.error.body === "object" && mutation.error.body !== null
              ? typeof (mutation.error.body as Record<string, unknown>).detail === "string"
                ? (mutation.error.body as { detail: string }).detail
                : mutation.error.message
              : mutation.error.message
            : mutation.error instanceof Error
            ? mutation.error.message
            : "Something went wrong. Please try again."}
        </Alert>
      )}

      {mutation.isSuccess && mode === "signup" && !("access_token" in mutation.data) && (
        <Alert variant="success">Account created successfully. You can now sign in.</Alert>
      )}

      <Button type="submit" className="w-full" disabled={mutation.isPending}>
        {mutation.isPending
          ? mode === "signup"
            ? "Creating account..."
            : "Signing in..."
          : mode === "signup"
          ? "Create account"
          : "Sign in"}
      </Button>
    </form>
  );
}

