"use client";

import { useEffect, useMemo, useState } from "react";
import { Button } from "./ui/button";
import { ThumbsUp, ThumbsDown, Trash2 } from "lucide-react";
import type { Poll } from "@/lib/polls";
import { castVote, deletePoll, dislikePoll, likePoll } from "@/lib/polls";
import { useAuthStore } from "@/stores/auth-store";
import type { AuthUser } from "@/lib/auth";
import { Alert } from "./ui/alert";

interface PollsCardProps {
  poll: Poll;
  onDeleted?: (pollId: number) => void;
  onUpdated?: (poll: Poll) => void;
}

export default function PollsCard({ poll, onDeleted, onUpdated }: PollsCardProps) {
  const token = useAuthStore((state) => state.token);
  const currentUser = useAuthStore((state) => state.user);
  const isOwner = currentUser?.id === poll.created_by;

  const initialSelectedOption = poll.my_vote_option_id ?? null;
  const [selectedOption, setSelectedOption] = useState<number | null>(initialSelectedOption);
  const [hasVoted, setHasVoted] = useState(initialSelectedOption !== null);
  const [userLiked, setUserLiked] = useState(false);
  const [userDisliked, setUserDisliked] = useState(false);
  const [currentLikes, setCurrentLikes] = useState(poll.likes);
  const [currentDislikes, setCurrentDislikes] = useState(poll.dislikes);
  const [options, setOptions] = useState(poll.options);
  const [error, setError] = useState<string | null>(null);
  const [isWorking, setIsWorking] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isDeleted, setIsDeleted] = useState(false);

  const totalVotes = useMemo(
    () => options.reduce((sum, option) => sum + option.votes, 0),
    [options]
  );

  useEffect(() => {
    setOptions(poll.options);
    setCurrentLikes(poll.likes);
    setCurrentDislikes(poll.dislikes);
    if (currentUser) {
      setUserLiked(poll.liked_by.some((user: AuthUser) => user.id === currentUser.id));
      setUserDisliked(poll.disliked_by.some((user: AuthUser) => user.id === currentUser.id));
    } else {
      setUserLiked(false);
      setUserDisliked(false);
    }
    const voteOptionId = poll.my_vote_option_id ?? null;
    setSelectedOption(voteOptionId);
    setHasVoted(voteOptionId !== null);
  }, [poll, currentUser]);

  // Calculate total votes
  const getPercentage = (votes: number) => {
    if (totalVotes === 0) return 0;
    return Math.round((votes / totalVotes) * 100);
  };

  const handleVote = async (optionId: number) => {
    if (!token) {
      setError("Please sign in to vote.");
      return;
    }

    try {
      setIsWorking(true);
      setError(null);
      const vote = await castVote(
        {
          poll_id: poll.id,
          option_id: optionId,
        },
        token
      );

      // Update selected option and vote status
      // Vote counts will be updated via SSE poll_updated event
      setSelectedOption(vote.option_id);
      setHasVoted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to cast vote.");
    } finally {
      setIsWorking(false);
    }
  };

  const handleLike = async () => {
    if (!token) {
      setError("Please sign in to like polls.");
      return;
    }

    try {
      setIsWorking(true);
      setError(null);
      const updatedPoll = await likePoll(poll.id, token);
      setCurrentLikes(updatedPoll.likes);
      setCurrentDislikes(updatedPoll.dislikes);
      setOptions(updatedPoll.options);
      if (currentUser) {
        setUserLiked(updatedPoll.liked_by.some((user: AuthUser) => user.id === currentUser.id));
        setUserDisliked(updatedPoll.disliked_by.some((user: AuthUser) => user.id === currentUser.id));
      } else {
        setUserLiked(false);
        setUserDisliked(false);
      }
      const voteOptionId = updatedPoll.my_vote_option_id ?? null;
      setSelectedOption(voteOptionId);
      setHasVoted(voteOptionId !== null);
      onUpdated?.(updatedPoll);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to like poll.");
    } finally {
      setIsWorking(false);
    }
  };

  const handleDislike = async () => {
    if (!token) {
      setError("Please sign in to dislike polls.");
      return;
    }

    try {
      setIsWorking(true);
      setError(null);
      const updatedPoll = await dislikePoll(poll.id, token);
      setCurrentLikes(updatedPoll.likes);
      setCurrentDislikes(updatedPoll.dislikes);
      setOptions(updatedPoll.options);
      if (currentUser) {
        setUserLiked(updatedPoll.liked_by.some((user: AuthUser) => user.id === currentUser.id));
        setUserDisliked(updatedPoll.disliked_by.some((user: AuthUser) => user.id === currentUser.id));
      } else {
        setUserLiked(false);
        setUserDisliked(false);
      }
      const voteOptionId = updatedPoll.my_vote_option_id ?? null;
      setSelectedOption(voteOptionId);
      setHasVoted(voteOptionId !== null);
      onUpdated?.(updatedPoll);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to dislike poll.");
    } finally {
      setIsWorking(false);
    }
  };

  const handleDelete = async () => {
    if (!token) {
      setError("Please sign in to delete polls.");
      return;
    }

    if (!confirm("Are you sure you want to delete this poll?")) {
      return;
    }

    try {
      setIsDeleting(true);
      setError(null);
      await deletePoll(poll.id, token);
      setIsDeleted(true);
      onDeleted?.(poll.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete poll.");
    } finally {
      setIsDeleting(false);
    }
  };

  if (isDeleted) {
    return null;
  }

  return (
    <div className="w-full max-w-2xl mx-auto bg-white dark:bg-zinc-900 rounded-lg shadow-lg p-6 space-y-4">
      {/* Poll Header */}
      <div className="space-y-2">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
              {poll.title}
            </h2>
            {poll.description && (
              <p className="text-sm text-zinc-600 dark:text-zinc-300">
                {poll.description}
              </p>
            )}
          </div>
          {(isOwner || currentUser?.is_admin) && (
            <Button
              type="button"
              variant="destructive"
              size="icon"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              <Trash2 className="h-4 w-4" />
              <span className="sr-only">Delete poll</span>
            </Button>
          )}
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <p className="text-sm">{error}</p>
        </Alert>
      )}

      {/* Poll Options */}
      <div className="space-y-3 mt-6">
        {options.map((option) => (
          <div key={option.id} className="w-full">
            {!hasVoted ? (
              // Before voting: Show plain option buttons
              <Button
                onClick={() => handleVote(option.id)}
                variant="outline"
                className="w-full h-auto py-4 px-6 text-left justify-start hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                disabled={isWorking}
              >
                <span className="text-base font-medium">{option.text}</span>
              </Button>
            ) : (
              // After voting: Show results with progress bar
              <div className="relative">
                <div 
                  className={`
                    relative overflow-hidden rounded-md border-2 p-4
                ${selectedOption === option.id 
                      ? 'border-blue-500 dark:border-blue-400' 
                      : 'border-zinc-200 dark:border-zinc-700'}
                  `}
                >
                  {/* Progress bar background */}
                  <div 
                    className={`
                      absolute inset-0 transition-all duration-500
                    ${selectedOption === option.id 
                        ? 'bg-blue-100 dark:bg-blue-900/30' 
                        : 'bg-zinc-100 dark:bg-zinc-800/50'}
                    `}
                    style={{ width: `${getPercentage(option.votes)}%` }}
                  />
                  
                  {/* Option content */}
                  <div className="relative flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-base font-medium text-zinc-900 dark:text-zinc-100">
                        {option.text}
                      </span>
                      {selectedOption === option.id && (
                        <span className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded-full">
                          Your vote
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-bold text-zinc-900 dark:text-zinc-100">
                        {getPercentage(option.votes)}%
                      </span>
                      <span className="text-sm text-zinc-600 dark:text-zinc-400">
                        ({option.votes} {option.votes === 1 ? 'vote' : 'votes'})
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Poll Footer */}
      {hasVoted && (
        <div className="pt-4 border-t border-zinc-200 dark:border-zinc-800">
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Total votes: <span className="font-semibold">{totalVotes}</span>
          </p>
        </div>
      )}

      {/* Like/Dislike Buttons */}
      <div className="pt-4 border-t border-zinc-200 dark:border-zinc-800">
        <div className="flex items-center gap-4">
          <Button
            onClick={handleLike}
            variant="outline"
            size="sm"
            className={`flex items-center gap-2 transition-colors ${
              userLiked 
                ? 'bg-blue-100 dark:bg-blue-900/30 border-blue-500 dark:border-blue-400 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-900/50' 
                : 'hover:bg-zinc-100 dark:hover:bg-zinc-800'
            }`}
            disabled={isWorking}
          >
            <ThumbsUp 
              className={`h-4 w-4 ${userLiked ? 'fill-current' : ''}`} 
            />
            <span className="font-semibold">{currentLikes}</span>
          </Button>

          <Button
            onClick={handleDislike}
            variant="outline"
            size="sm"
            className={`flex items-center gap-2 transition-colors ${
              userDisliked 
                ? 'bg-red-100 dark:bg-red-900/30 border-red-500 dark:border-red-400 text-red-700 dark:text-red-300 hover:bg-red-200 dark:hover:bg-red-900/50' 
                : 'hover:bg-zinc-100 dark:hover:bg-zinc-800'
            }`}
            disabled={isWorking}
          >
            <ThumbsDown 
              className={`h-4 w-4 ${userDisliked ? 'fill-current' : ''}`} 
            />
            <span className="font-semibold">{currentDislikes}</span>
          </Button>
        </div>
      </div>

      {/* Poll Metadata */}
      <div className="pt-2 flex items-center justify-between text-xs text-zinc-500 dark:text-zinc-500">
        <span>
          Created: {new Date(poll.created_at).toLocaleDateString("en-US", { month: "2-digit", day: "2-digit", year: "numeric" })}
        </span>
        {poll.updated_at && (
          <span>
            Updated: {new Date(poll.updated_at).toLocaleDateString("en-US", { month: "2-digit", day: "2-digit", year: "numeric" })}
          </span>
        )}
        {poll.poll_expires_at && (
          <span>
            Expires: {new Date(poll.poll_expires_at).toLocaleDateString("en-US", { month: "2-digit", day: "2-digit", year: "numeric" })}
          </span>
        )}
      </div>
    </div>
  );
}
