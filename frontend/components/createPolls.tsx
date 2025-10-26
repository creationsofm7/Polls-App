"use client";

import { useForm, Controller, type ControllerRenderProps, type FieldError as RHFFieldError } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Field, FieldGroup, FieldLabel, FieldError } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { createPoll } from "@/lib/polls";
import { useAuthStore } from "@/stores/auth-store";
import { Alert } from "./ui/alert";
import { useState } from "react";
import { PlusCircle, Loader2 } from "lucide-react";

interface CreatePollProps {
  onPollCreated?: () => void;
}

// Schema
const pollSchema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters"),
  description: z.string().optional(),
  options: z
    .array(z.string().min(1, "Option cannot be empty"))
    .min(2, "At least 2 options required"),
  poll_expires_at: z.string().optional(),
});

type PollFormValues = z.infer<typeof pollSchema>;

export default function CreatePoll({ onPollCreated }: CreatePollProps = {}) {
  const token = useAuthStore((state) => state.token);
  const form = useForm<PollFormValues>({
    resolver: zodResolver(pollSchema),
    defaultValues: {
      title: "",
      description: "",
      options: ["", ""],
      poll_expires_at: "",
    },
  });

  const {
    handleSubmit,
    control,
    watch,
    getValues,
    setValue,
    formState: { isSubmitting },
  } = form;

  const [serverError, setServerError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const onSubmit = async (data: PollFormValues) => {
    if (!token) {
      setServerError("You must be logged in to create a poll.");
      return;
    }

    try {
      setServerError(null);
      setSuccessMessage(null);

      const payload = {
        title: data.title,
        description: data.description?.trim() ? data.description.trim() : null,
        poll_expires_at: data.poll_expires_at?.trim()
          ? new Date(data.poll_expires_at).toISOString()
          : null,
        options: data.options
          .map((text) => text.trim())
          .filter(Boolean)
          .map((text) => ({ text })),
      };

      await createPoll(payload, token);
      form.reset();

      if (onPollCreated) {
        onPollCreated();
        setSuccessMessage(null);
      } else {
        setSuccessMessage("Poll created successfully!");
      }
    } catch (err) {
      setServerError(
        err instanceof Error ? err.message : "Failed to create poll. Please try again."
      );
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Header Section */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <div className="flex items-center justify-center w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
            <PlusCircle className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          </div>
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">Create a New Poll</h2>
        </div>
        <p className="text-zinc-600 dark:text-zinc-400">
          Share your question with the community and gather valuable insights
        </p>
      </div>

      <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-lg p-6">

      {!token && (
        <Alert variant="destructive" className="mb-4">
          <p className="font-medium">Sign in required</p>
          <p className="text-xs text-zinc-600 dark:text-zinc-300">
            Log in to create a poll.
          </p>
        </Alert>
      )}

      {serverError && (
        <Alert variant="destructive" className="mb-4">
          <p className="text-sm">{serverError}</p>
        </Alert>
      )}

      {successMessage && (
        <Alert variant="success" className="mb-4">
          <p className="text-sm">{successMessage}</p>
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <FieldGroup>
          {/* Poll Title - Using Controller for Field integration */}
          <Controller
            name="title"
            control={control}
            render={({ field, fieldState }: { field: ControllerRenderProps<PollFormValues, "title">; fieldState: { invalid: boolean; error?: RHFFieldError } }) => (
              <Field data-invalid={fieldState.invalid}>
                <FieldLabel>Poll Title</FieldLabel>
                <Input
                  placeholder="What's your question?"
                  {...field}
                />
                <FieldError>{fieldState.error?.message}</FieldError>
              </Field>
            )}
          />

          {/* Poll Description */}
          <Controller
            name="description"
            control={control}
            render={({ field, fieldState }: { field: ControllerRenderProps<PollFormValues, "description">; fieldState: { invalid: boolean; error?: RHFFieldError } }) => (
              <Field data-invalid={fieldState.invalid}>
                <FieldLabel>Description (Optional)</FieldLabel>
                <Textarea
                  placeholder="Add more context..."
                  {...field}
                />
                <FieldError>{fieldState.error?.message}</FieldError>
              </Field>
            )}
          />

          {/* Poll Options */}
          <div className="space-y-4">
            <FieldLabel>Poll Options</FieldLabel>
            {/* eslint-disable-next-line react-hooks/incompatible-library */}
            {watch("options").map((_: string, index: number) => (
              <Controller
                key={index}
                name={`options.${index}` as const}
                control={control}
                render={({ field, fieldState }: { field: ControllerRenderProps<PollFormValues, `options.${number}`>; fieldState: { invalid: boolean; error?: RHFFieldError } }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <Input
                      placeholder={`Option ${index + 1}`}
                      {...field}
                    />
                    <FieldError>{fieldState.error?.message}</FieldError>
                  </Field>
                )}
              />
            ))}
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => {
                const currentOptions = getValues("options");
                setValue("options", [...currentOptions, ""]);
              }}
            >
              + Add Option
            </Button>
          </div>

          {/* Poll expiration */}
          <Controller
            name="poll_expires_at"
            control={control}
            render={({
              field,
              fieldState,
            }: {
              field: ControllerRenderProps<PollFormValues, "poll_expires_at">;
              fieldState: { invalid: boolean; error?: RHFFieldError };
            }) => (
              <Field data-invalid={fieldState.invalid}>
                <FieldLabel>Poll expiration (optional)</FieldLabel>
                <Input
                  type="datetime-local"
                  {...field}
                />
                <FieldError>{fieldState.error?.message}</FieldError>
              </Field>
            )}
          />
        </FieldGroup>

        <div className="flex justify-end gap-3 pt-4">
          <Button type="button" variant="outline" onClick={() => form.reset()}>
            Clear
          </Button>
          <Button type="submit" disabled={isSubmitting || !token} className="flex items-center space-x-2">
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Creating...</span>
              </>
            ) : (
              <>
                <PlusCircle className="h-4 w-4" />
                <span>Create Poll</span>
              </>
            )}
          </Button>
        </div>
      </form>
      </div>
    </div>
  );
}