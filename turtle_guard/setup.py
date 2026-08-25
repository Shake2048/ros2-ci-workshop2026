from setuptools import find_packages, setup

package_name = 'turtle_guard'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    tests_require=['pytest'],
    zip_safe=True,
    maintainer='Robotics Lab',
    maintainer_email='lab@example.com',
    description='A tiny velocity-limiting safety node, used as a CI/CD teaching example.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'velocity_guard = turtle_guard.velocity_guard_node:main',
        ],
    },
)
