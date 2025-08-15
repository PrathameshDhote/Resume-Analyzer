import * as React from "react"

// Ensure this path is correct for your project structure (e.g., src/lib/utils.js)
import { cn } from "../../lib/utils"

// Removed TypeScript interface definition
// export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

// Removed TypeScript type annotations for React.forwardRef
const Textarea = React.forwardRef(({ className, ...props }, ref) => {
  return (
    <textarea
      className={cn(
        "flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
      ref={ref}
      {...props}
    />
  )
})
Textarea.displayName = "Textarea"

export { Textarea }
