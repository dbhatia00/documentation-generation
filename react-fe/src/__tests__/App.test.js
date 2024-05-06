import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import App from '../App';

describe('App component', () => {
  test('renders login button if not logged in', () => {
    const { getByText } = render(<App />);
    const loginButton = getByText('Login with Github: Generate your own project documentation');
    expect(loginButton).toBeInTheDocument();
  });

  test('renders fetch input box if logged in', async () => {
    // Mocking local storage to simulate logged in state
    const mockAccessToken = 'mock_access_token';
    const mockLocalStorage = {
      getItem: jest.fn().mockImplementation((key) => {
        if (key === 'accessToken') return mockAccessToken;
        return null;
      }),
      removeItem: jest.fn(),
    };
    Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

    const { getByText, getByPlaceholderText } = render(<App />);
    const fetchInputBox = getByPlaceholderText('{username}/{repo name}');
    expect(fetchInputBox).toBeInTheDocument();

    const fetchButton = getByText('Fetch');
    expect(fetchButton).toBeInTheDocument();
  });
  
});
