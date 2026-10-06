#pragma once
// Station JNI publishes reconciled catalogs by swapping its two live item vectors.
// Cover completions change only revision and artwork fields; they must not rewrite
// the whole diagnostic TSV. UI revision handling continues independently.
constexpr bool catalogIdentityChanged(int priorRevision, unsigned long priorItems,
 unsigned long priorSize, unsigned long items, unsigned long size) {
 return priorRevision < 0 || priorItems != items || priorSize != size;
}
