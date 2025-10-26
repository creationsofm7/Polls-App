# Polls - Interactive Polling Platform

A modern, professional polling platform built with Next.js, React, and TypeScript. Create, share, and participate in polls with real-time results and community engagement features.

## Features

- **Create Polls**: Design custom polls with multiple options, descriptions, and expiration dates
- **Real-time Voting**: Cast votes and see live results with percentage breakdowns
- **Community Engagement**: Like/dislike polls and track community sentiment
- **User Management**: Secure authentication with user profiles
- **Responsive Design**: Beautiful, mobile-first interface with dark mode support
- **Professional UI**: Clean, modern design with intuitive navigation

## Tech Stack

- **Frontend**: Next.js 16, React 19, TypeScript
- **Styling**: Tailwind CSS with custom design system
- **State Management**: Zustand for client state
- **Forms**: React Hook Form with Zod validation
- **UI Components**: Radix UI primitives with custom styling
- **Icons**: Lucide React
- **HTTP Client**: Custom API client with error handling

## Getting Started

1. **Install dependencies**:
   ```bash
   pnpm install
   ```

2. **Start the development server**:
   ```bash
   pnpm dev
   ```

3. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
├── app/                    # Next.js app directory
│   ├── layout.tsx         # Root layout with metadata
│   ├── page.tsx           # Main application page
│   └── providers.tsx      # React Query and other providers
├── components/            # Reusable UI components
│   ├── auth/             # Authentication components
│   ├── ui/               # Base UI components
│   ├── createPolls.tsx   # Poll creation form
│   ├── myPolls.tsx       # User's polls management
│   ├── pollsCard.tsx     # Individual poll display
│   └── wall.tsx          # Polls feed
├── lib/                  # Utility libraries
│   ├── api-client.ts     # HTTP client configuration
│   ├── auth.ts           # Authentication utilities
│   └── polls.ts          # Poll-related API functions
└── stores/               # State management
    └── auth-store.ts     # Authentication state
```

## Key Components

### PollsCard
The main poll display component featuring:
- Interactive voting with real-time results
- Like/dislike functionality
- Progress bars and percentage displays
- Owner/admin controls for poll management

### CreatePoll
Professional poll creation form with:
- Form validation using Zod schemas
- Dynamic option management
- Optional expiration dates
- Real-time form feedback

### Wall & MyPolls
Feed components with:
- Professional loading states
- Empty state designs
- Error handling
- Responsive layouts

## Design System

The application uses a consistent design system with:
- **Colors**: Professional blue accent with zinc grays
- **Typography**: Geist font family for modern readability
- **Spacing**: Consistent spacing scale
- **Components**: Reusable UI primitives
- **Dark Mode**: Full dark mode support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.