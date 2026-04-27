from setuptools import find_packages, setup
import os
from glob import glob
package_name = 'asif_mpme'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bitdrones',
    maintainer_email='23ldy@queensu.ca',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'Asif_MPME_Node = asif_mpme.Asif_MPME_Node:main',
            'simple_pose_node = asif_mpme.simple_pose_node:main',

        ],
    },
)
