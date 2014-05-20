#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by René Meusel
This file is part of the CernVM File System auxiliary tools.
"""

import unittest
import StringIO
import datetime
from dateutil.tz import tzutc

import cvmfs


class TestManifest(unittest.TestCase):
    def setUp(self):
        self.sane_manifest = StringIO.StringIO('\n'.join([
            'C600230b0ba7620426f2e898f1e1f43c5466efe59',
            'D3600',
            'L0000000000000000000000000000000000000000',
            'Natlas.cern.ch',
            'Rd41d8cd98f00b204e9800998ecf8427e',
            'S4264',
            'T1390395640',
            'X0b457ac12225018e0a15330364c20529e15012ab',
            '--',
            '0f41e81ed7faade7ad1dafc4be6fa3f7fdc51b05',
            '(§3Êõ0ð¬a˜‚Û}Y„¨x3q    ·EÖ£%²é³üŽ6Ö+>¤XâñÅ=_X‡Ä'
        ]))

        self.unknown_field_manifest = StringIO.StringIO('\n'.join([
            'C600230b0ba7620426f2e898f1e1f43c5466efe59',
            'D3600',
            'L0000000000000000000000000000000000000000',
            'Natlas.cern.ch',
            'Rd41d8cd98f00b204e9800998ecf8427e',
            'S4264',
            'Qi_am_unexpected!'
        ]))

        self.minimal_manifest_entries = [
            'C600230b0ba7620426f2e898f1e1f43c5466efe59',
            'Rd41d8cd98f00b204e9800998ecf8427e',
            'D3600',
            'S4264',
            'Natlas.cern.ch'
        ]

        self.minimal_manifest = StringIO.StringIO('\n'.join(
            self.minimal_manifest_entries) + '\n--')


    def test_manifest_creation(self):
        manifest = cvmfs.Manifest(self.sane_manifest)
        last_modified = datetime.datetime(2014, 1, 22, 13, 0, 40, tzinfo=tzutc())
        self.assertTrue(hasattr(manifest, 'root_catalog'))
        self.assertTrue(hasattr(manifest, 'ttl'))
        self.assertTrue(hasattr(manifest, 'micro_catalog'))
        self.assertTrue(hasattr(manifest, 'repository_name'))
        self.assertTrue(hasattr(manifest, 'root_hash'))
        self.assertTrue(hasattr(manifest, 'revision'))
        self.assertTrue(hasattr(manifest, 'last_modified'))
        self.assertTrue(hasattr(manifest, 'certificate'))
        self.assertFalse(hasattr(manifest, 'history_database'))
        self.assertEqual('600230b0ba7620426f2e898f1e1f43c5466efe59', manifest.root_catalog)
        self.assertEqual(3600                                      , manifest.ttl)
        self.assertEqual('0000000000000000000000000000000000000000', manifest.micro_catalog)
        self.assertEqual('atlas.cern.ch'                           , manifest.repository_name)
        self.assertEqual('d41d8cd98f00b204e9800998ecf8427e'        , manifest.root_hash)
        self.assertEqual(4264                                      , manifest.revision)
        self.assertEqual(last_modified                             , manifest.last_modified)
        self.assertEqual('0b457ac12225018e0a15330364c20529e15012ab', manifest.certificate)


    def test_minimal_manifest(self):
        manifest = cvmfs.Manifest(self.minimal_manifest)
        self.assertTrue(hasattr(manifest, 'root_catalog'))
        self.assertTrue(hasattr(manifest, 'root_hash'))
        self.assertTrue(hasattr(manifest, 'ttl'))
        self.assertTrue(hasattr(manifest, 'revision'))
        self.assertTrue(hasattr(manifest, 'repository_name'))
        self.assertEqual('600230b0ba7620426f2e898f1e1f43c5466efe59', manifest.root_catalog)
        self.assertEqual('d41d8cd98f00b204e9800998ecf8427e'        , manifest.root_hash)
        self.assertEqual(3600                                      , manifest.ttl)
        self.assertEqual(4264                                      , manifest.revision)
        self.assertEqual('atlas.cern.ch'                           , manifest.repository_name)


    def test_unknown_manifest_field(self):
        self.assertRaises(cvmfs.UnknownManifestField,
                          cvmfs.Manifest, self.unknown_field_manifest)


    def test_invalid_manifest(self):
        for i in range(len(self.minimal_manifest_entries)):
            incomplete_manifest_entries = list(self.minimal_manifest_entries)
            del incomplete_manifest_entries[i]
            incomplete_manifest = StringIO.StringIO('\n'.join(incomplete_manifest_entries) + '\n--')
            self.assertRaises(cvmfs.ManifestValidityError,
                              cvmfs.Manifest, incomplete_manifest)
