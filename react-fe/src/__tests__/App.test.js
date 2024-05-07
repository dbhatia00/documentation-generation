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
  
});
