import { instance } from '@/api/api.interceptor'
import { IGetUsers } from './user.types'

export const UserService = {
	async getAll() {
		const { data } = await instance<IGetUsers>({
			method: 'GET',
		})
		return data
	},
}
