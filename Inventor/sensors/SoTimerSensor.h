#ifndef COIN_SOTIMERSENSOR_H
#define COIN_SOTIMERSENSOR_H

/**************************************************************************\
 *
 *  This file is part of the Coin 3D visualization library.
 *  Copyright (C) 1998-2003 by Systems in Motion.  All rights reserved.
 *
 *  This library is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU General Public License
 *  ("GPL") version 2 as published by the Free Software Foundation.
 *  See the file LICENSE.GPL at the root directory of this source
 *  distribution for additional information about the GNU GPL.
 *
 *  For using Coin with software that can not be combined with the GNU
 *  GPL, and for taking advantage of the additional benefits of our
 *  support services, please contact Systems in Motion about acquiring
 *  a Coin Professional Edition License.
 *
 *  See <URL:http://www.coin3d.org> for  more information.
 *
 *  Systems in Motion, Teknobyen, Abels Gate 5, 7030 Trondheim, NORWAY.
 *  <URL:http://www.sim.no>.
 *
\**************************************************************************/

#include <Inventor/sensors/SoTimerQueueSensor.h>

#ifdef __PIVY__
%rename(SoTimerSensor_scb_v) SoTimerSensor::SoTimerSensor(SoSensorCB * func, void * data);

%feature("shadow") SoTimerSensor::SoTimerSensor %{
def __init__(self,*args):
   if len(args) == 2:
      args = (args[0], (args[0], args[1]))
      self.this = apply(_pivy.new_SoTimerSensor_scb_v,args)
      self.thisown = 1
      return
   self.this = apply(_pivy.new_SoTimerSensor,args)
   self.thisown = 1
%}
#endif

class COIN_DLL_API SoTimerSensor : public SoTimerQueueSensor {
  typedef SoTimerQueueSensor inherited;

public:
  SoTimerSensor(void);
  SoTimerSensor(SoSensorCB * func, void * data);
  virtual ~SoTimerSensor(void);

  void setBaseTime(const SbTime & base);
  const SbTime & getBaseTime(void) const;
  void setInterval(const SbTime & interval);
  const SbTime & getInterval(void) const;

  virtual void schedule(void);
  virtual void unschedule(void);
  void reschedule(const SbTime & schedtime);

private:
  virtual void trigger(void);

  SbTime base, interval;
  SbBool setbasetime;
  SbBool istriggering;
};

#endif // !COIN_SOTIMERSENSOR_H