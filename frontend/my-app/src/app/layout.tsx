import Header from '@/components/ui/header/Header'
import { SITE_NAME } from '@/constants/app.constants'
import Providers from '@/providers/Providers'
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
	title: {
		absolute: SITE_NAME,
		template: `%s | ${SITE_NAME}`,
	},
}
export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode
}>) {
	return (
		<html lang='en'>
			<body>
				<Providers>
					<div className='bg-[#2E3239] h-auto'>
						<Header />
					</div>
					<main>{children}</main>
				</Providers>
			</body>
		</html>
	)
}
