// Local storage utilities

/**
 * Get item from localStorage
 */
export function getStorageItem(key: string): string | null {
  if (typeof window === 'undefined') return null;
  try {
    return localStorage.getItem(key);
  } catch (error) {
    console.warn(`Failed to read from localStorage: ${key}`, error);
    return null;
  }
}

/**
 * Set item in localStorage
 */
export function setStorageItem(key: string, value: string): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(key, value);
  } catch (error) {
    console.warn(`Failed to write to localStorage: ${key}`, error);
  }
}

/**
 * Remove item from localStorage
 */
export function removeStorageItem(key: string): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.warn(`Failed to remove from localStorage: ${key}`, error);
  }
}

/**
 * Clear all localStorage
 */
export function clearStorage(): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.clear();
  } catch (error) {
    console.warn('Failed to clear localStorage', error);
  }
}

/**
 * Get parsed JSON from localStorage
 */
export function getStorageJSON<T>(key: string): T | null {
  try {
    const item = getStorageItem(key);
    return item ? JSON.parse(item) : null;
  } catch (error) {
    console.warn(`Failed to parse JSON from localStorage: ${key}`, error);
    return null;
  }
}

/**
 * Set JSON to localStorage
 */
export function setStorageJSON<T>(key: string, value: T): void {
  try {
    setStorageItem(key, JSON.stringify(value));
  } catch (error) {
    console.warn(`Failed to stringify/store JSON in localStorage: ${key}`, error);
  }
}
