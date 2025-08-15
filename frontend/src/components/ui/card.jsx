import * as React from "react"

// Ensure this path is correct for your project structure (e.g., src/lib/utils.js)
import { cn } from "../../lib/utils"

// Removed TypeScript type annotations for React.forwardRef
const Card = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("rounded-lg border bg-card text-card-foreground shadow-sm", className)} {...props} />
))
Card.displayName = "Card"

// Removed TypeScript type annotations for React.forwardRef
const CardHeader = React.forwardRef(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} />
  ),
)
CardHeader.displayName = "CardHeader"

// Removed TypeScript type annotations for React.forwardRef and children type
const CardTitle = React.forwardRef(
  ({ className, children, ...props }, ref) => ( // `children` is now implicitly `any` or `React.Node`
    <h3 ref={ref} className={cn("text-2xl font-semibold leading-none tracking-tight", className)} {...props}>
      {children} {/* Render children */}
    </h3>
  ),
)
CardTitle.displayName = "CardTitle"

// Removed TypeScript type annotations for React.forwardRef
const CardDescription = React.forwardRef(
  ({ className, ...props }, ref) => (
    <p ref={ref} className={cn("text-sm text-muted-foreground", className)} {...props} />
  ),
)
CardDescription.displayName = "CardDescription"

// Removed TypeScript type annotations for React.forwardRef
const CardContent = React.forwardRef(
  ({ className, ...props }, ref) => <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />,
)
CardContent.displayName = "CardContent"

// Removed TypeScript type annotations for React.forwardRef
const CardFooter = React.forwardRef(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex items-center p-6 pt-0", className)} {...props} />
  ),
)
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
