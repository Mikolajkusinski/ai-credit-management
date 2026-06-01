import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ModelCard from '../ModelCard';

describe('ModelCard (smoke)', () => {
  it('renders the model name and prediction label', () => {
    render(
      <ModelCard
        modelName="Random Forest"
        prediction={{ defaultProbability: 0.42, prediction: 'NO DEFAULT' }}
        icon="🌲"
      />,
    );

    expect(screen.getByRole('heading', { name: /random forest/i })).toBeInTheDocument();
    expect(screen.getByText(/no default/i)).toBeInTheDocument();
  });
});
