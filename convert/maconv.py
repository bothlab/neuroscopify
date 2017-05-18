#!/usr/bin/env python3
#
# Copyright (C) 2012-2016 Matthias Klumpp <matthias@tenstral.net>
#
# Licensed under the GNU Lesser General Public License Version 3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the license, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import json
from xml.etree.ElementTree import Element, SubElement, ElementTree

from .convert_rhd import rhd2dat
from .convert_positions import convert_positions


#readable dtypes and their bit depth
DTYPES = dict(int16='16',
        int32='32',
        int64='64')

def create_neuroscope_channel_data(result):
    '''
    Creates the XML for channel information.
    '''

    s_dtype = str(result['amplifier_data'].dtype)
    assert s_dtype in DTYPES

    n_amp_channels = len(result['amplifier_channels'])
    n_dig_in_channels = len(result['board_dig_in_channels'])

    n_channels = n_amp_channels + n_dig_in_channels

    parameters = Element('parameters')
    parameters.set('version', '1.0')
    parameters.set('creator', 'ma-neuroscopify')

    # position file
    n_files = SubElement(parameters, 'files')
    n_file = SubElement(n_files, 'file')
    SubElement(n_file, 'extension').text = 'pos'
    SubElement(n_file, 'samplingRate').text = '20' # FIXME: Make configurable

    # video data
    n_video = SubElement(parameters, 'video')
    SubElement(n_video, 'width').text = '1280'
    SubElement(n_video, 'height').text = '1024' # FIXME: read from video info file
    SubElement(n_video, 'positionsBackground').text = '1'

    acq = SubElement(parameters, 'acquisitionSystem')
    SubElement(acq, 'nBits').text = DTYPES[s_dtype]
    SubElement(acq, 'nChannels').text = str(n_channels)
    SubElement(acq, 'samplingRate').text = str(result['frequency_parameters']['amplifier_sample_rate'])
    SubElement(acq, 'voltageRange').text = '20'
    SubElement(acq, 'amplification').text = '1000'
    SubElement(acq, 'offset').text = '0'
    fp = SubElement(parameters, 'fieldPotentials')
    SubElement(fp, 'lfpSamplingRate').text = '1250'
    anatdes = SubElement(parameters, 'anatomicalDescription')
    chngrp = SubElement(anatdes, 'channelGroup')
    grp = SubElement(chngrp, 'group')
    for i in range(n_channels):
        channel = SubElement(grp, 'channel')
        channel.set('skip', '0')
        channel.text = str(i)
        if i == n_amp_channels - 1:
            # new group for digital channels
            grp = SubElement(chngrp, 'group')
    SubElement(parameters, 'spikeDetection')
    neuroscope = SubElement(parameters, 'neuroscope')
    neuroscope.set('version', '2.0.0')
    misc = SubElement(neuroscope, 'miscellaneous')
    SubElement(misc, 'screenGain').text = '2.0'
    SubElement(misc, 'traceBackgroundImage')
    vid = SubElement(neuroscope, 'video')
    SubElement(vid, 'rotate').text = '0'
    SubElement(vid, 'flip').text = '0'
    SubElement(vid, 'videoImage')
    SubElement(vid, 'positionsBackground').text = '0'
    spikes = SubElement(neuroscope, 'spikes')
    SubElement(spikes, 'nSamples').text = '32'
    SubElement(spikes, 'peakSampleIndex').text = '16'
    channels = SubElement(neuroscope, 'channels')
    for i in range(n_channels):
        channelcolors = SubElement(channels, 'channelColors')
        SubElement(channelcolors, 'channel').text = str(i)
        if i < n_amp_channels:
            SubElement(channelcolors, 'color').text = '#0080ff'
            SubElement(channelcolors, 'anatomyColor').text = '#0080ff'
            SubElement(channelcolors, 'spikeColor').text = '#0080ff'
        else:
            SubElement(channelcolors, 'color').text = '#87ff00'
            SubElement(channelcolors, 'anatomyColor').text = '#87ff00'
            SubElement(channelcolors, 'spikeColor').text = '#87ff00'
        channeloffset = SubElement(channels, 'channelOffset')
        SubElement(channeloffset, 'channel').text = str(i)
        SubElement(channeloffset, 'defaultOffset').text = "0"

    return ElementTree(parameters)


def create_neuroscope_settings_data(result, pos_fname):
    '''
    Creates the XML for NeuroScope (display) settings.
    '''

    n_amp_channels = len(result['amplifier_channels'])
    n_dig_in_channels = len(result['board_dig_in_channels'])

    n_channels = n_amp_channels + n_dig_in_channels

    settings = Element('neuroscope')
    settings.set('version', '2.0.0')

    # position file
    if pos_fname:
        nFiles = SubElement(settings, 'files')
        nFile = SubElement(nFiles, 'file')
        SubElement(nFile, 'type').text = '3'
        SubElement(nFile, 'url').text = pos_fname

    displays = SubElement(settings, 'displays')
    display = SubElement(displays, 'display')

    SubElement(display, 'startTime').text = '0'
    SubElement(display, 'duration').text = '1000'

    channelPositions = SubElement(display, 'channelPositions')
    for i in range(n_channels):
        chanPos = SubElement(channelPositions, 'channelPosition')
        SubElement(chanPos, 'channel').text = str(i)
        if i < n_amp_channels:
            # gain for digital channels
            SubElement(chanPos, 'gain').text = '0'
        else:
            SubElement(chanPos, 'gain').text = '-20'

    return ElementTree(settings)


def save_neuroscope_metadata(dat_fname, rhd_result, pos_fname, override_settings = True):
    nsx_fname = os.path.splitext(dat_fname)[0] + ".xml"
    xml_tree = create_neuroscope_channel_data(rhd_result)
    xml_tree.write(nsx_fname, xml_declaration=True, short_empty_elements=False)

    if override_settings:
        ns_fname = os.path.splitext(dat_fname)[0] + ".nrs"
        xml_tree = create_neuroscope_settings_data(rhd_result, pos_fname)
        xml_tree.write(ns_fname, xml_declaration=True, short_empty_elements=False)


def convert_ma(root_path, subject, time, experiment, no_settings_override):
    '''
    Convert MazeAmaze data and directory so Nauroscope can read the data.
    '''

    exp_root_path = os.path.join(root_path, subject, time, experiment)
    manifest_fname = os.path.join(exp_root_path, "manifest.json")
    if not os.path.isfile(manifest_fname):
        raise Exception("Manifest file '{}' not found.".format(manifest_fname))

    intan_rhd_file = None
    ephys_dir = os.path.join(exp_root_path, "intan")
    for fname in os.listdir(ephys_dir):
        if fname.endswith(".rhd"):
            intan_rhd_file = os.path.join(ephys_dir, fname)

    if not intan_rhd_file:
        raise Exception("No Intan ephys data was found.")

    output_dir = os.path.join(exp_root_path, "neuroscope")
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    dat_fname = os.path.join(output_dir, "channels.dat")
    rhd_result = rhd2dat(intan_rhd_file, dat_fname)

    pos_fname = os.path.join(output_dir, "positions.pos")
    pos_input_fname = os.path.join(exp_root_path, "video", "{}_positions.csv".format(subject))
    if os.path.isfile(pos_input_fname):
        convert_positions(pos_input_fname, pos_fname, 20)

    save_neuroscope_metadata(dat_fname, rhd_result, pos_fname, not no_settings_override)

    return output_dir


def convert_rhd(rhd_file, output_dir, override):
    '''
    Convert a plain Intan RHD file into a .dat file and Neuroscope metadata.
    '''

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    dat_fname = os.path.join(output_dir, "{}.dat".format(os.path.splitext(os.path.basename(rhd_file))[0]))
    if os.path.isfile(dat_fname) and not override:
        return dat_fname

    rhd_result = rhd2dat(rhd_file, dat_fname)
    save_neuroscope_metadata(dat_fname, rhd_result, None, override)

    return dat_fname
