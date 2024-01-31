'use client'

import { UserService } from '@/services/user/user.service'
import { useQuery } from '@tanstack/react-query'

export function Home() {
	const { data } = useQuery({
		queryKey: ['get users'],
		queryFn: () => UserService.getAll(),
	})
	console.log('data: ', data?.msg.Users)

	return (
		<div className='p-2 text-white'>
			Home Page
			<div>dsadsada</div>
			<p>asdadasd</p>
		</div>
	)
}
