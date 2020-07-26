# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#!/usr/bin/env python3

import argparse
import os
import sys
import yaml
import yamlloader





def apply_overlay(base, overlay, append=False):
    """

    :param base: Dict of yaml to apply changes to. Gets mutated
    :param overlay: Dict of changes. Identical structure to base
    :param append: True to append, false to replace values
    :return: base dict with changes applied. Mutation of base input dict
    """


    for k1, v1 in overlay.items():
        if not isinstance(v1, dict):
            if append:
                base[k1] += v1
            else:
                base[k1] = v1


        else:
            for k2, v2 in v1.items():
                if not isinstance(v2, dict):
                    if append:
                        base[k1][k2] += v2
                    else:
                        base[k1][k2] = v2


                else:
                    for k3, v3 in v2.items():
                        if not isinstance(v3, dict):
                            if append:
                                base[k1][k2][k3] += v3
                            else:
                                base[k1][k2][k3] = v3


                        else:
                            for k4, v4 in v3.items():
                                if not isinstance(v4, dict):
                                    if append:
                                        base[k1][k2][k3][k4] += v4
                                    else:
                                        base[k1][k2][k3][k4] = v4
                                else:
                                    raise NotImplementedError("Exceeds current yaml max depth")
    return base






if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Create a variant of a yaml by applying overlays which describe changes')
    parser.add_argument('base_yaml_path',
                        help="Yaml to use as base. If '-' is given, will read from stdin instead.")
    parser.add_argument('overlays', metavar='N', type=str, nargs='+',
                        help='Overlays to apply in sequential order')
    parser.add_argument('--overlay_dir', type=str,
                        help='Path to dir containing all overlays. Can be passed in through OVERLAY_BASE_DIR '
                             'environmental variable. If both env var and cli arg are present, cli arg wins.')

    args = parser.parse_args()

    overlay_base_dir = None
    if "OVERLAY_DIR" in os.environ.keys() and os.environ['OVERLAY_DIR'] is not None:
        overlay_base_dir = os.environ['OVERLAY_DIR']
    if args.overlay_dir is not None:
        overlay_base_dir = args.overlay_dir

    if args.base_yaml_path == '-':
        s = "".join([l for l in sys.stdin])
        values = yaml.load(s, Loader=yamlloader.ordereddict.CLoader)
    else:
        with open(args.base_yaml_path, 'r') as f:
            values = yaml.load(f, Loader=yamlloader.ordereddict.CLoader)

    overlay_dicts = []
    for overlay in args.overlays:
        overlay_path = f'{overlay}.yaml'
        if overlay_base_dir is not None:
            overlay_path = os.path.join(overlay_base_dir, overlay_path)

        with open(overlay_path) as f:
            overlay_dicts.append(yaml.load(f, Loader=yamlloader.ordereddict.CLoader))

    for overlay_dict in overlay_dicts:
        if 'append' in overlay_dict.keys():
            values = apply_overlay(values, overlay_dict['append'], append=True)
        if 'set' in overlay_dict.keys():
            values = apply_overlay(values, overlay_dict['set'], append=False)

    print(yaml.dump(values,
                    Dumper=yamlloader.ordereddict.CDumper,
                    default_flow_style=False))