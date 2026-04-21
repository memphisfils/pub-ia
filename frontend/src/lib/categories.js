export const CATEGORY_OPTIONS = [
  { value: 'achat_tech', label: 'Tech' },
  { value: 'achat_beaute', label: 'Beauté' },
  { value: 'achat_finance', label: 'Finance' },
  { value: 'achat_assurance', label: 'Assurance' },
  { value: 'achat_auto', label: 'Auto' },
  { value: 'achat_sport', label: 'Sport' },
  { value: 'achat_voyage', label: 'Voyage' },
  { value: 'achat_mode', label: 'Mode' },
  { value: 'achat_sante', label: 'Santé' },
  { value: 'achat_alimentation', label: 'Alimentation' },
  { value: 'achat_immobilier', label: 'Immobilier' },
  { value: 'achat_formation', label: 'Formation' },
  { value: 'achat_logiciel', label: 'Logiciel' },
  { value: 'achat_maison', label: 'Maison' },
  { value: 'achat_animaux', label: 'Animaux' },
];

const CATEGORY_LABELS = Object.fromEntries(
  CATEGORY_OPTIONS.map(({ value, label }) => [value, label]),
);

export function getCategoryLabel(category) {
  return CATEGORY_LABELS[category] || category || 'Non définie';
}
