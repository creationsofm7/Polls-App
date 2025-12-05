"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ChangeEvent } from "react";
import PollsCard from "./pollsCard";
import { listMyPolls, type Poll, type PollSortBy } from "@/lib/polls";
import { useAuthStore } from "@/stores/auth-store";
import { Alert } from "./ui/alert";
import { User, Loader2, PlusCircle } from "lucide-react";
import { Button } from "./ui/button";
import { API_BASE_URL } from "@/lib/api-client";

type ConnectionState = "connecting" | "connected" | "disconnected" | "paused";

interface MyPollsProps {
  isActive?: boolean;
}

export default function MyPolls({ isActive = true }: MyPollsProps) {
  const token = useAuthStore((state) => state.token);
  const user = useAuthStore((state) => state.user);
  const [polls, setPolls] = useState<Poll[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connectionState, setConnectionState] = useState<ConnectionState>(
    isActive && token ? "connecting" : "paused"
  );
  const [sortBy, setSortBy] = useState<PollSortBy>("created_at");
  const firstLoadRef = useRef(true);
  const isAuthenticated = Boolean(token);

  const handlePollDeleted = useCallback((pollId: number) => {
    setPolls((prev) => prev.filter((poll) => poll.id !== pollId));
  }, []);

  const upsertPoll = useCallback(
    (incomingPoll: Poll) => {
      if (!user || incomingPoll.created_by !== user.id) {
        return;
      }

      setPolls((prev) => {
        const existingIndex = prev.findIndex((poll) => poll.id === incomingPoll.id);

        const nextPoll = (() => {
          if (existingIndex === -1) {
            return incomingPoll;
          }

          const existing = prev[existingIndex];
          if (
            existing.my_vote_option_id !== undefined &&
            (incomingPoll.my_vote_option_id === undefined ||
              incomingPoll.my_vote_option_id === null)
          ) {
            return {
              ...incomingPoll,
              my_vote_option_id: existing.my_vote_option_id,
            };
          }

          return incomingPoll;
        })();

        if (existingIndex === -1) {
          const next = [nextPoll, ...prev];
          return next.slice(0, 20);
        }

        const next = [...prev];
        next[existingIndex] = nextPoll;
        return next;
      });
    },
    [user]
  );

  useEffect(() => {
    let ignore = false;
    let source: EventSource | null = null;
    let reconnectTimer: number | null = null;
    let intervalId: number | null = null;
    let currentHandlers: {
      handleCreated: (event: MessageEvent) => void;
      handleUpdated: (event: MessageEvent) => void;
      handleDeleted: (event: MessageEvent) => void;
    } | null = null;

    // Early return if not authenticated or not active
    if (!token || !user || !isActive) {
      setPolls([]);
      setIsLoading(false);
      setConnectionState(!isActive ? "paused" : "disconnected");
      return;
    }

    if (typeof window === "undefined") {
      setConnectionState(isAuthenticated ? "connecting" : "paused");
      return undefined;
    }

    firstLoadRef.current = true;

    const fetchMyPolls = async () => {
      if (ignore) return;
      
      const isFirstLoad = firstLoadRef.current;
      if (isFirstLoad) {
        setIsLoading(true);
      }

      try {
        setError(null);
        const response = await listMyPolls(
          { sort_by: sortBy, limit: 20, offset: 0 },
          token
        );
        if (!ignore) {
          setPolls((prev) => {
            if (prev.length === 0) {
              return response;
            }

            const preserved = new Map<number, number | null | undefined>();
            for (const poll of prev) {
              preserved.set(poll.id, poll.my_vote_option_id);
            }

            return response.map((poll: Poll) => {
              if (
                (poll.my_vote_option_id === undefined || poll.my_vote_option_id === null) &&
                preserved.has(poll.id)
              ) {
                return {
                  ...poll,
                  my_vote_option_id: preserved.get(poll.id) ?? null,
                };
              }
              return poll;
            });
          });
        }
      } catch (err) {
        if (!ignore) {
          setError(err instanceof Error ? err.message : "Failed to load your polls");
        }
      } finally {
        if (!ignore && isFirstLoad) {
          setIsLoading(false);
          firstLoadRef.current = false;
        } else if (!ignore) {
          setIsLoading(false);
        }
      }
    };

    intervalId = window.setInterval(fetchMyPolls, 60_000);
    void fetchMyPolls();

    // Only setup EventSource if authenticated
    if (isAuthenticated && token) {
      // EventSource doesn't support custom headers, so we need to pass token as query param
      const streamUrl = `${API_BASE_URL}/api/polls/stream`;

      const cleanupStream = () => {
        if (source && currentHandlers) {
          source.removeEventListener("poll_created", currentHandlers.handleCreated);
          source.removeEventListener("poll_updated", currentHandlers.handleUpdated);
          source.removeEventListener("poll_deleted", currentHandlers.handleDeleted);
          source.close();
          source = null;
          currentHandlers = null;
        }
      };

      const openStream = () => {
        if (ignore) {
          return;
        }

        setConnectionState("connecting");

        // Clean up any existing connection properly
        cleanupStream();

        source = new EventSource(streamUrl);

        const handleCreated = (event: MessageEvent) => {
          if (ignore) {
            return;
          }

          try {
            const payload = JSON.parse(event.data) as { poll: Poll };
            if (user && payload.poll.created_by === user.id) {
              upsertPoll(payload.poll);
            }
          } catch (parseError) {
            console.error("Failed to process poll_created event", parseError);
          }
        };

        const handleUpdated = (event: MessageEvent) => {
          if (ignore) {
            return;
          }

          try {
            const payload = JSON.parse(event.data) as { poll: Poll };
            // Check if poll belongs to current user
            if (user && payload.poll.created_by === user.id) {
              upsertPoll(payload.poll);
            }
          } catch (parseError) {
            console.error("Failed to process poll_updated event", parseError);
          }
        };

        const handleDeleted = (event: MessageEvent) => {
          if (ignore) {
            return;
          }

          try {
            const payload = JSON.parse(event.data) as { poll_id: number };
            handlePollDeleted(payload.poll_id);
          } catch (parseError) {
            console.error("Failed to process poll_deleted event", parseError);
          }
        };

        // Store handlers for cleanup
        currentHandlers = { handleCreated, handleUpdated, handleDeleted };

        source.addEventListener("poll_created", handleCreated);
        source.addEventListener("poll_updated", handleUpdated);
        source.addEventListener("poll_deleted", handleDeleted);

        source.onopen = () => {
          if (!ignore) {
            setConnectionState("connected");
          }
        };

        source.onerror = () => {
          if (ignore) {
            return;
          }

          setConnectionState("disconnected");

          // Clean up the failed connection properly
          cleanupStream();

          // Only reconnect if still active and not ignoring
          if (!ignore && reconnectTimer === null) {
            reconnectTimer = window.setTimeout(() => {
              reconnectTimer = null;
              if (!ignore) {
                openStream();
              }
            }, 5_000);
          }
        };
      };

      openStream();

      // Cleanup function
      return () => {
        ignore = true;
        if (reconnectTimer !== null) {
          window.clearTimeout(reconnectTimer);
          reconnectTimer = null;
        }
        cleanupStream();
        if (intervalId !== null) {
          window.clearInterval(intervalId);
          intervalId = null;
        }
      };
    } else {
      setConnectionState("paused");
      
      // Cleanup function for non-authenticated case
      return () => {
        ignore = true;
        if (intervalId !== null) {
          window.clearInterval(intervalId);
          intervalId = null;
        }
      };
    }
  }, [isActive, isAuthenticated, sortBy, user, upsertPoll, handlePollDeleted]);

  const handlePollUpdated = useCallback((updatedPoll: Poll) => {
    upsertPoll(updatedPoll);
  }, [upsertPoll]);

  const handleSortChange = useCallback((event: ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value as PollSortBy;
    setSortBy(value);
  }, []);

  const connectionBadge = useMemo(() => {
    if (!isAuthenticated) {
      return { label: "Sign in for live updates", color: "bg-zinc-400" };
    }

    if (!isActive) {
      return { label: "Paused", color: "bg-zinc-400" };
    }

    const label =
      connectionState === "connected"
        ? "Live updates"
        : connectionState === "connecting"
        ? "Connecting…"
        : connectionState === "paused"
        ? "Paused"
        : "Reconnecting…";

    const label =
      NoconnectionState === "connected"
        ? "Live updates"
        : NOconnectionState === "connecting"
        ? "Connecting…"
        : NoconnectionState === "paused"
        ? "Paused"
        : "Reconnecting…";
    const color =
      connectionState === "connected"
        ? "bg-green-500"
        : connectionState === "connecting"
        ? "bg-amber-500"
        : connectionState === "paused"
        ? "bg-zinc-400"
        : "bg-red-500";

    return { label, color };
  }, [connectionState, isActive, isAuthenticated]);

  if (!token) {
    return (
      <div className="w-full max-w-4xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <div className="flex items-center justify-center w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <User className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            </div>
            <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">My Polls</h2>
          </div>
          <p className="text-zinc-600 dark:text-zinc-400">
            Manage and track your created polls
          </p>
        </div>
        
        <Alert variant="destructive">
          <p className="font-medium">Sign in required</p>
          <p className="text-xs text-zinc-600 dark:text-zinc-300">
            You need to be logged in to view your polls.
          </p>
        </Alert>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Header Section */}
      <div className="mb-8 space-y-2">
        <div className="flex flex-col items-start gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <User className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            </div>
            <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">My Polls</h2>
          </div>
          <div className="flex items-center gap-3 text-xs text-zinc-500 dark:text-zinc-400">
            <div className="flex items-center gap-2">
              <span className={`inline-flex h-2.5 w-2.5 rounded-full ${connectionBadge.color}`} />
              <span className="font-medium whitespace-nowrap">{connectionBadge.label}</span>
            </div>
            <label className="flex items-center gap-2">
              <span className="text-[11px] uppercase tracking-wide text-zinc-400 dark:text-zinc-500">
                Sort by
              </span>
              <select
                value={sortBy}
                onChange={handleSortChange}
                className="rounded-md border border-zinc-300 bg-white px-2 py-1 text-xs font-medium text-zinc-700 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200"
              >
                <option value="created_at">Most Recent</option>
                <option value="likes">Most Liked</option>
              </select>
            </label>
          </div>
        </div>
        <p className="text-zinc-600 dark:text-zinc-400">
          Manage and track your created polls
        </p>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center space-x-3 text-zinc-500 dark:text-zinc-400">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Loading your polls...</span>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <p className="font-medium">Unable to load your polls</p>
          <p className="text-xs text-zinc-600 dark:text-zinc-300">{error}</p>
        </Alert>
      )}

      {/* Empty State */}
      {!isLoading && !error && polls.length === 0 && (
        <div className="text-center py-12">
          <div className="flex items-center justify-center w-16 h-16 bg-zinc-100 dark:bg-zinc-800 rounded-full mx-auto mb-4">
            <User className="h-8 w-8 text-zinc-400" />
          </div>
          <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            No polls created yet
          </h3>
          <p className="text-zinc-600 dark:text-zinc-400 mb-6">
            Start engaging with the community by creating your first poll!
          </p>
          <Button className="flex items-center space-x-2 mx-auto">
            <PlusCircle className="h-4 w-4" />
            <span>Create Your First Poll</span>
          </Button>
        </div>
      )}

      {/* Polls Grid */}
      {!isLoading && !error && polls.length > 0 && (
        <div className="space-y-6">
          {polls.map((poll) => (
            <PollsCard
              key={poll.id}
              poll={poll}
              onUpdated={handlePollUpdated}
              onDeleted={handlePollDeleted}
            />
          ))}
        </div>
      )}
    </div>
  );
}
