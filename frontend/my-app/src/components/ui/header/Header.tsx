'use client'
import Link from 'next/link'
import { useState } from 'react'
import { Search } from '../search/Search'

export default function Header() {
	const [isAdminPanel, setIsAdminPanel] = useState(true)
	return (
		<header
			className='p-8 grid'
			style={{
				gridTemplateColumns: '1fr 2fr 1fr 1fr 1fr',
			}}
		>
			<Link href='/'>Logo Image</Link>
			<Search />
			{isAdminPanel && <h2>Admin</h2>}
			<div>Header Cart</div>
			<div>Header Profile</div>
		</header>
	)
}
