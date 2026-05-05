import { writable } from 'svelte/store';

// User type definition
export interface User {
	user_id: number;
	name: string;
	email: string;
	org_id?: number;
	created_at: string;
	role: string;
	status: string;
}

// User store to manage user state across components
export const user = writable<User | null>(null);

// Initialize user from sessionStorage if available
if (typeof window !== 'undefined') {
	const userData = sessionStorage.getItem('user');
	if (userData) {
		try {
			user.set(JSON.parse(userData));
		} catch (e) {
			console.error('Failed to parse user data:', e);
			sessionStorage.removeItem('user');
		}
	}
}

// Helper function to set user data
export function setUser(userData: User) {
	user.set(userData);
	if (typeof window !== 'undefined') {
		sessionStorage.setItem('user', JSON.stringify(userData));
	}
}

// Helper function to clear user data
export function clearUser() {
	user.set(null);
	if (typeof window !== 'undefined') {
		sessionStorage.removeItem('user');
	}
}