'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { PropsWithChildren } from 'react'

const queryClient = new QueryClient()

export default function Providers({ children }: PropsWithChildren<unknown>) {
	return (
		<QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
	)
}
