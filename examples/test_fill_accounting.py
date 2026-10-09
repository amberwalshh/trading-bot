"""Synthetic offline tests for the isolated public accounting component."""
import copy
import unittest

from fill_accounting import ReconciliationError, held_quantity, observe, quantity, result


def order(filled, average=None, total=10, status='WORKING'):
    return {'filled_quantity': filled, 'filled_price': average,
            'total_quantity': total, 'status': status}


def fixture(direction='long'):
    active = {'ids': {'master': 'entry', 'target': 'target', 'stop': 'stop'},
              'direction': direction, 'quantity': 10}
    details = {'entry': order(10, 100, status='FILLED'),
               'target': order(0), 'stop': order(0)}
    return active, details


class FillAccountingTests(unittest.TestCase):
    def test_repeated_snapshot_is_idempotent(self):
        active, details = fixture()
        self.assertEqual(observe(active, details), 10)
        first = copy.deepcopy(active)
        self.assertEqual(observe(active, details), 10)
        self.assertEqual(active, first)

    def test_partial_entry_tracks_remaining_quantity(self):
        active, details = fixture()
        details['entry'] = order(4, 100)
        self.assertEqual(observe(active, details), 4)
        self.assertEqual(active['entry_remaining_quantity'], 6)
        self.assertFalse(result(active)['pnl_verified'])

    def test_weighted_partial_exits_long_and_short(self):
        for direction, expected in [('long', 4), ('short', -4)]:
            with self.subTest(direction=direction):
                active, details = fixture(direction)
                details['target'] = order(4, 102)
                details['stop'] = order(6, 99.33333333333333)
                self.assertEqual(observe(active, details), 0)
                self.assertTrue(result(active)['pnl_verified'])
                self.assertAlmostEqual(result(active)['pnl_before_fees'], expected)

    def test_open_position_is_not_reported_as_realized(self):
        active, details = fixture()
        observe(active, details)
        self.assertIsNone(result(active)['pnl_before_fees'])

    def test_missing_actual_fill_price_rejects_atomically(self):
        active, details = fixture()
        details['entry']['filled_price'] = None
        before = copy.deepcopy(active)
        with self.assertRaises(ReconciliationError):
            observe(active, details)
        self.assertEqual(active, before)

    def test_cumulative_quantity_cannot_go_backwards(self):
        active, details = fixture()
        observe(active, details)
        details['entry'] = order(9, 100)
        with self.assertRaises(ReconciliationError):
            observe(active, details)

    def test_exit_cannot_exceed_owned_entry(self):
        active, details = fixture()
        details['target'] = order(10, 102, status='FILLED')
        details['stop'] = order(1, 99)
        with self.assertRaises(ReconciliationError):
            observe(active, details)

    def test_manual_quantity_change_leaves_pnl_unverified(self):
        active, details = fixture()
        details['target'] = order(10, 102, status='FILLED')
        observe(active, details)
        active['manual_quantity_change'] = True
        self.assertFalse(result(active)['pnl_verified'])

    def test_invalid_whole_share_quantities(self):
        for value in [None, -1, 1.5, float('nan'), float('inf')]:
            with self.subTest(value=value), self.assertRaises(ReconciliationError):
                quantity(value)

    def test_owned_position_direction_mismatch_rejects(self):
        with self.assertRaises(ReconciliationError):
            held_quantity([{'symbol': 'TEST', 'quantity': -10}], 'TEST', 'long')


if __name__ == '__main__':
    unittest.main()
