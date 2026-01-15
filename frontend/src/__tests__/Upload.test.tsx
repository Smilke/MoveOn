import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import Upload from '../components/Upload';

describe('Upload component', () => {
  beforeEach(() => {
    // reset fetch mock
    (global as any).fetch = undefined;
  });

  it('sends selected file to the API and shows success', async () => {
    const fakeResponse = { filename: 'uploaded.mp4' };
    (global as any).fetch = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(fakeResponse) }));

    const { container } = render(<Upload />);

    const file = new File(['dummy content'], 'video.mp4', { type: 'video/mp4' });
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    await userEvent.upload(input, file);

    const button = screen.getByText('Enviar') as HTMLButtonElement;
    await userEvent.click(button);

    await waitFor(() => {
      expect((global as any).fetch).toHaveBeenCalled();
      expect(screen.getByText(/Upload concluído:/)).toBeInTheDocument();
    });
  });
});
