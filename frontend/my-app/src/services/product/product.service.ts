import { instance } from '@/api/api.interceptor'
import { IProduct } from './product.types'

const PRODUCTS = 'products'

export const ProductService = {
	async getAll() {
		const { data } = await instance<IProduct[]>({
			url: PRODUCTS,
			method: 'GET',
		})
		return data
	},
}
