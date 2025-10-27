import { apiFetch } from "./api-client";
import type { AuthUser } from "./auth";

export type PollSortBy = "created_at" | "likes";

export interface PollOption {
  id: number;
  text: string;
  votes: number;
}

export interface PollOptionPayload {
  text: string;
}

export interface Poll {
  id: number;
  title: string;
  description: string | null;
  likes: number;
  dislikes: number;
  poll_expires_at: string | null;
  created_at: string;
  updated_at: string | null;
  created_by: number;
  creator: AuthUser;
  options: PollOption[];
  liked_by: AuthUser[];
  disliked_by: AuthUser[];
  my_vote_option_id?: number | null;
}

export interface CreatePollPayload {
  title: string;
  description?: string | null;
  poll_expires_at?: string | null;
  options: PollOptionPayload[];
}

export interface PollListRequest {
  sort_by: PollSortBy;
  limit?: number;
  offset?: number;
}

export interface VotePayload {
  poll_id: number;
  option_id: number;
}

export interface Vote {
  id: number;
  user_id: number;
  poll_id: number;
  option_id: number;
  created_at: string;
}

export async function createPoll(payload: CreatePollPayload, token: string) {
  return apiFetch<Poll>("/api/polls/", {
    method: "POST",
    body: payload,
    token,
  });
}

export async function listPolls(payload: PollListRequest, token?: string | null) {
  return apiFetch<Poll[]>("/api/polls/list", {
    method: "POST",
    body: payload,
    token: token ?? undefined,
  });
}

export async function listMyPolls(payload: PollListRequest, token: string) {
  return apiFetch<Poll[]>("/api/polls/mine", {
    method: "POST",
    body: payload,
    token,
  });
}

export async function deletePoll(pollId: number | string, token: string) {
  await apiFetch<void>(`/api/polls/${pollId}`, {
    method: "DELETE",
    token,
  });
}

export async function likePoll(pollId: number | string, token: string) {
  return apiFetch<Poll>(`/api/polls/${pollId}/like`, {
    method: "POST",
    token,
  });
}

export async function dislikePoll(pollId: number | string, token: string) {
  return apiFetch<Poll>(`/api/polls/${pollId}/dislike`, {
    method: "POST",
    token,
  });
}

export async function castVote(payload: VotePayload, token: string) {
  return apiFetch<Poll>("/api/votes/", {
    method: "POST",
    body: payload,
    token,
  });
}

// Server-Sent Events (SSE) for real-time poll updates
export interface PollStreamEvent {
  type: "poll_created" | "poll_updated" | "poll_deleted";
  poll?: Poll;
  poll_id?: number;
}

export function createPollStream(
  onEvent: (event: PollStreamEvent) => void,
  onError?: (error: Error) => void
): EventSource {
  const eventSource = new EventSource(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/polls/stream`);

  eventSource.addEventListener("poll_created", (event) => {
    try {
      const data = JSON.parse(event.data);
      onEvent({ type: "poll_created", poll: data.poll });
    } catch (error) {
      onError?.(error as Error);
    }
  });

  eventSource.addEventListener("poll_updated", (event) => {
    try {
      const data = JSON.parse(event.data);
      onEvent({ type: "poll_updated", poll: data.poll });
    } catch (error) {
      onError?.(error as Error);
    }
  });

  eventSource.addEventListener("poll_deleted", (event) => {
    try {
      const data = JSON.parse(event.data);
      onEvent({ type: "poll_deleted", poll_id: data.poll_id });
    } catch (error) {
      onError?.(error as Error);
    }
  });

  eventSource.onerror = (event) => {
    onError?.(new Error("EventSource connection error"));
  };

  return eventSource;
}

