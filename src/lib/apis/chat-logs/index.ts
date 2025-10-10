import { WEBUI_API_BASE_URL } from '$lib/constants';

export const getChatLogs = async (
	token: string,
	filter?: object,
	admin?: boolean
) => {
	let error = null;

	const searchParams = new URLSearchParams();

	if (filter) {
		Object.entries(filter).forEach(([key, value]) => {
			if (value !== undefined && value !== null) {
				searchParams.append(key, value.toString());
			}
		});
	}

	const endpoint = admin ? '/chat-logs/admin' : '/chat-logs';
	
	const res = await fetch(`${WEBUI_API_BASE_URL}${endpoint}?${searchParams.toString()}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const deleteChatLogs = async (
	token: string,
	filter?: object,
	admin?: boolean
) => {
	let error = null;

	const searchParams = new URLSearchParams();

	if (filter) {
		Object.entries(filter).forEach(([key, value]) => {
			if (value !== undefined && value !== null) {
				searchParams.append(key, value.toString());
			}
		});
	}

	const endpoint = admin ? '/chat-logs/admin' : '/chat-logs';
	
	const res = await fetch(`${WEBUI_API_BASE_URL}${endpoint}?${searchParams.toString()}`, {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};
