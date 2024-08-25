import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';

Widget stackBacground() => Stack(
      alignment: Alignment.bottomRight,
      children: [
        Lottie.asset(
          'assets/animation/ppmana.json',
          fit: BoxFit.fill,
          height: double.infinity,
          width: double.infinity,
        ),
        Lottie.asset(
          'assets/animation/p2p.json',
          fit: BoxFit.fill,
          // height: double.infinity,
          // width: double.infinity,
        ),
        Positioned.fill(
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 40, sigmaY: 30),
            child: const SizedBox(),
          ),
        ),
      ],
    );
