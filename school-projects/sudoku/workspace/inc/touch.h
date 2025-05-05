/* File: TOUCH.H */

#ifndef __TOUCH_H
#define __TOUCH_H

#ifndef __PIXELS
#define __PIXELS
#define  XPIXELS   240	// The left edge of the screen is at x = 0
#define  YPIXELS   320	// The top edge of the screen is at y = 0
#endif

void TS_Init(void) ;
int	TS_Touched(void) ;	// returns non-zero if touched
int	TS_GetX(void) ;		// returns 0 to XPIXELS - 1
int	TS_GetY(void) ;		// returns 0 to YPIXELS - 1

#ifndef  __FIXTS__
int __fixts__ = 0 ;         // Invert y coordinate if MB1075E detected
#else
#if     (__FIXTS__ == 0)
int __fixts__ = 1 ;         // don't perform test nor invert y coordinate
#elif   (__FIXTS__ == 1)
int __fixts__ = 2 ;         // don't perform test but invert y coordinate
#endif
#endif

#endif
