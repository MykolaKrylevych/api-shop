import cn from 'clsx'
import { FC, PropsWithChildren } from 'react'
import s from './Heading.module.css'

interface IHeading {
	size: '2xl' | '3xl' | '4xl'
	className?: string
}

const Heading: FC<PropsWithChildren<IHeading>> = ({
	size = '4xl',
	className,
	children,
}) => {
	return (
		<h1
			className={cn(s.heading, {
				[s.heading_2xl]: size === '2xl',
				[s.heading_3xl]: size === '3xl',
				[s.heading_4xl]: size === '4xl',
			})}
		>
			{children}
		</h1>
	)
}
export default Heading
