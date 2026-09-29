import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { SettingsSheet } from '../components/SettingsSheet';

describe('SettingsSheet Component', () => {
  it('toggles show answer while I speak and changes text size', () => {
    const handleToggle = vi.fn();
    const handleTextSize = vi.fn();
    const handleClose = vi.fn();

    render(
      <SettingsSheet
        isOpen={true}
        onClose={handleClose}
        showDraftsWhileSpeaking={true}
        onToggleDraftsWhileSpeaking={handleToggle}
        textSize="normal"
        onChangeTextSize={handleTextSize}
      />
    );

    expect(screen.getByText('Settings')).toBeDefined();
    expect(screen.getByText('Show answer while I speak')).toBeDefined();

    // Toggle switch
    const switchBtn = screen.getByRole('switch');
    fireEvent.click(switchBtn);
    expect(handleToggle).toHaveBeenCalledWith(false);

    // Text size change
    const largeBtn = screen.getByText('Large');
    fireEvent.click(largeBtn);
    expect(handleTextSize).toHaveBeenCalledWith('large');

    // Close button
    const closeBtn = screen.getByLabelText('Close settings');
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalled();
  });
});
