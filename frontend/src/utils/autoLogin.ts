/**
 * Auto-login utility for demo purposes
 * In production, replace with a proper login page
 */

import { login } from '../api/authService';
import { isAuthenticated } from '../api/auth';

/**
 * Automatically login as admin if not already authenticated
 */
export async function ensureAuthenticated(): Promise<boolean> {
  // Check if already authenticated
  if (isAuthenticated()) {
    return true;
  }

  try {
    // Auto-login as admin (for demo purposes)
    await login({
      username: 'admin@hellio.com',
      password: 'admin123',
    });
    console.log('Auto-logged in as admin');
    return true;
  } catch (error) {
    console.error('Auto-login failed:', error);
    return false;
  }
}
