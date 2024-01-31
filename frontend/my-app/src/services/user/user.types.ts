export type IUser = {
	user_email: string
	id: number
	username: string
	balance: number
	password: string
}

export interface IGetUsers {
	msg: {
		Users: IUser[]
	}
}
