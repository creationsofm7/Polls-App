import * as React from "react";
import { cn } from "@/lib/utils";

const alertVariants = {
  default: "bg-muted text-muted-foreground",
  destructive: "text-destructive border-destructive/50 bg-destructive/10",
  success: "border-green-500/50 bg-green-500/10 text-green-300",
};

export interface AlertProps extends React.ComponentPropsWithoutRef<"div"> {
  variant?: keyof typeof alertVariants;
}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant = "default", ...props }, ref) => (
    <div
      ref={ref}
      role="alert"
      className={cn(
        "border-l-4 rounded-md px-3 py-2 text-sm",
        alertVariants[variant],
        className
      )}
      {...props}
    />
  )
);

Alert.displayName = "Alert";

export { Alert };

