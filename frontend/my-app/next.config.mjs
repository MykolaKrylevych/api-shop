/** @type {import('next').NextConfig} */
const nextConfig = {
	reactStrictMode: true,
	env: {
		SERVER_URL: process.env.SERVER_URL,
		APP_URL: process.env.APP_URL,
	},
	async headers() {
		return [
			{
				source: '/(.*)',
				headers: [
					{
						key: 'Access-Control-Allow-Origin',
						value: '*',
					},
					{
						key: 'Access-Control-Allow-Methods',
						value: 'GET,OPTIONS,PATCH,DELETE,POST,PUT',
					},
					{
						key: 'Access-Control-Allow-Headers',
						value:
							'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version',
					},
				],
			},
		]
	},
}

export default nextConfig